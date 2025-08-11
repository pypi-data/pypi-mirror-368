import atexit
import queue
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, List, Optional

import requests


class TrackingEvent:
    def __init__(
        self,
        event_type: str,
        trace_id: str,
        timestamp: float,
        data: Dict[str, Any],
        generation_id: Optional[str] = None,
        span_id: Optional[str] = None,
    ):
        self.type = event_type
        self.trace_id = trace_id
        self.generation_id = generation_id
        self.span_id = span_id
        self.timestamp = timestamp
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "traceId": self.trace_id,
            "timestamp": int(self.timestamp * 1000),  # Convert to milliseconds
            "data": self.data,
        }
        if self.generation_id:
            result["generationId"] = self.generation_id
        if self.span_id:
            result["spanId"] = self.span_id
        return result


class KairozTracking:
    def __init__(
        self, api_key: str, base_url: Optional[str] = None, max_queue_size: int = 1000
    ):
        self.api_key = api_key
        self.base_url = base_url or "https://api.kairozai.com"
        self.max_queue_size = max_queue_size

        self.event_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

        self.is_online = True
        self.worker_thread = None
        self.shutdown_event = threading.Event()

        # Start background worker
        self._start_worker()

        # Register cleanup
        atexit.register(self._cleanup)

    def _start_worker(self):
        """Start the background worker thread"""
        self.worker_thread = threading.Thread(target=self._process_events, daemon=True)
        self.worker_thread.start()

    def track(self, event: TrackingEvent) -> None:
        """Track an event - non-blocking"""
        if not self.is_online:
            return

        try:
            self.event_queue.put_nowait(event)
        except queue.Full:
            # If queue is full, remove oldest and add new
            try:
                self.event_queue.get_nowait()
                self.event_queue.put_nowait(event)
            except queue.Empty:
                pass

    def _process_events(self):
        """Background thread worker for processing events"""
        batch = []
        last_flush = time.time()
        batch_size = 20
        flush_interval = 2.0  # 2 seconds

        while not self.shutdown_event.is_set():
            try:
                # Wait for event with timeout
                event = self.event_queue.get(timeout=1.0)
                batch.append(event)

                # Flush if batch is full or enough time has passed
                should_flush = (
                    len(batch) >= batch_size
                    or time.time() - last_flush > flush_interval
                )

                if should_flush:
                    self._send_batch(batch)
                    batch.clear()
                    last_flush = time.time()

            except queue.Empty:
                # Timeout - flush any pending batch
                if batch:
                    self._send_batch(batch)
                    batch.clear()
                    last_flush = time.time()

    def _send_batch(self, events: List[TrackingEvent]) -> None:
        """Send batch to API - never raise exceptions to main thread"""
        try:
            payload = {"events": [event.to_dict() for event in events]}

            response = self.session.post(
                f"{self.base_url}/api/tracking/batch", json=payload, timeout=3.0
            )
            response.raise_for_status()

        except requests.exceptions.ConnectionError:
            self.is_online = False
            # Retry after 30 seconds
            threading.Timer(30.0, lambda: setattr(self, "is_online", True)).start()
        except Exception as e:
            # Log error but never raise to main thread
            if hasattr(sys, "stderr"):
                print(f"Kairoz tracking failed: {e}", file=sys.stderr)

    def _flush_remaining(self) -> None:
        """Flush any remaining events"""
        batch = []
        try:
            while True:
                event = self.event_queue.get_nowait()
                batch.append(event)
        except queue.Empty:
            pass

        if batch:
            self._send_batch(batch)

    def _cleanup(self) -> None:
        """Cleanup when shutting down"""
        self.shutdown_event.set()
        self._flush_remaining()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)

    def flush(self) -> None:
        """Force flush of current queue (useful for testing)"""
        self._flush_remaining()

    def destroy(self) -> None:
        """Explicitly destroy the tracker"""
        self._cleanup()


# Global tracking instance
_global_tracking: Optional[KairozTracking] = None


def initialize_tracking(api_key: str, base_url: Optional[str] = None) -> KairozTracking:
    """Initialize global tracking instance"""
    global _global_tracking
    _global_tracking = KairozTracking(api_key, base_url)
    return _global_tracking


def get_tracking() -> Optional[KairozTracking]:
    """Get the global tracking instance"""
    return _global_tracking


def _generate_id() -> str:
    """Generate a unique UUID"""
    return str(uuid.uuid4())


# Context managers for structured tracking
@contextmanager
def trace(
    name: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
):
    """Context manager for tracking a trace"""
    tracking = get_tracking()
    if not tracking:
        yield TraceContextStub()
        return

    trace_id = _generate_id()

    # Start trace
    tracking.track(
        TrackingEvent(
            event_type="trace_start",
            trace_id=trace_id,
            timestamp=time.time(),
            data={
                "name": name,
                "userId": user_id,
                "sessionId": session_id,
                "metadata": metadata or {},
                "tags": tags or [],
            },
        )
    )

    try:
        yield TraceContext(tracking, trace_id)
    finally:
        # End trace
        tracking.track(
            TrackingEvent(
                event_type="trace_end",
                trace_id=trace_id,
                timestamp=time.time(),
                data={},
            )
        )


class TraceContext:
    def __init__(self, tracking: KairozTracking, trace_id: str):
        self.tracking = tracking
        self.trace_id = trace_id

    @contextmanager
    def generation(
        self,
        name: str,
        model: str,
        input_data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Context manager for tracking a generation within this trace"""
        generation_id = _generate_id()
        _start_ts = time.time()

        # Start generation
        self.tracking.track(
            TrackingEvent(
                event_type="generation_start",
                trace_id=self.trace_id,
                generation_id=generation_id,
                timestamp=_start_ts,
                data={
                    "name": name,
                    "model": model,
                    "input": input_data,
                    "metadata": metadata or {},
                },
            )
        )

        gen_ctx = GenerationContext(self.tracking, self.trace_id, generation_id, _start_ts)

        try:
            yield gen_ctx
        finally:
            # End generation with cached data
            self.tracking.track(
                TrackingEvent(
                    event_type="generation_end",
                    trace_id=self.trace_id,
                    generation_id=generation_id,
                    timestamp=time.time(),
                    data={
                        "output": getattr(gen_ctx, "_output", None),
                        "usage": getattr(gen_ctx, "_usage", None),
                        "metadata": getattr(gen_ctx, "_metadata", {}) or {},
                        # Milliseconds epoch; service does new Date(ms)
                        "startTime": int(getattr(gen_ctx, "_start_time", _start_ts) * 1000),
                    },
                )
            )

    @contextmanager
    def span(
        self,
        name: str,
        input_data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Context manager for tracking a span within this trace"""
        span_id = _generate_id()
        _start_ts = time.time()

        # Start span
        self.tracking.track(
            TrackingEvent(
                event_type="span_start",
                trace_id=self.trace_id,
                span_id=span_id,
                timestamp=_start_ts,
                data={"name": name, "input": input_data, "metadata": metadata or {}},
            )
        )

        span_ctx = SpanContext(self.tracking, self.trace_id, span_id, _start_ts)

        try:
            yield span_ctx
        finally:
            # End span with cached data
            self.tracking.track(
                TrackingEvent(
                    event_type="span_end",
                    trace_id=self.trace_id,
                    span_id=span_id,
                    timestamp=time.time(),
                    data={
                        "output": getattr(span_ctx, "_output", None),
                        "metadata": getattr(span_ctx, "_metadata", {}) or {},
                        # Milliseconds epoch; service does new Date(ms)
                        "startTime": int(getattr(span_ctx, "_start_time", _start_ts) * 1000),
                    },
                )
            )


class GenerationContext:
    def __init__(self, tracking: KairozTracking, trace_id: str, generation_id: str, start_time: float):
        self.tracking = tracking
        self.trace_id = trace_id
        self.generation_id = generation_id
        self._start_time = start_time
        # Cached fields for final end event
        self._output: Any = None
        self._usage: Optional[Dict[str, Any]] = None
        self._metadata: Dict[str, Any] = {}

    def update(
        self,
        output: Any = None,
        usage: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Cache output/usage/metadata to be included on generation_end."""
        if output is not None:
            self._output = output
        if usage is not None:
            self._usage = usage
        if metadata is not None:
            # Merge metadata
            if not isinstance(self._metadata, dict):
                self._metadata = {}
            self._metadata.update(metadata)


class SpanContext:
    def __init__(self, tracking: KairozTracking, trace_id: str, span_id: str, start_time: float):
        self.tracking = tracking
        self.trace_id = trace_id
        self.span_id = span_id
        self._start_time = start_time
        # Cached fields for final end event
        self._output: Any = None
        self._metadata: Dict[str, Any] = {}

    def update(self, output: Any = None, metadata: Optional[Dict[str, Any]] = None):
        """Cache output/metadata to be included on span_end."""
        if output is not None:
            self._output = output
        if metadata is not None:
            if not isinstance(self._metadata, dict):
                self._metadata = {}
            self._metadata.update(metadata)


class TraceContextStub:
    """Stub context when tracking is not initialized"""

    @contextmanager
    def generation(self, *args, **kwargs):
        yield GenerationContextStub()

    @contextmanager
    def span(self, *args, **kwargs):
        yield SpanContextStub()


class GenerationContextStub:
    def update(self, *args, **kwargs):
        pass


class SpanContextStub:
    def update(self, *args, **kwargs):
        pass


def add_score(
    name: str,
    value: float,
    trace_id: Optional[str] = None,
    generation_id: Optional[str] = None,
    comment: Optional[str] = None,
):
    """Add a score to a trace or generation"""
    tracking = get_tracking()
    if not tracking:
        return

    tracking.track(
        TrackingEvent(
            event_type="score",
            trace_id=trace_id or "",
            timestamp=time.time(),
            data={
                "name": name,
                "value": value,
                "traceId": trace_id,
                "generationId": generation_id,
                "comment": comment,
            },
        )
    )


# Decorator for automatic tracking
def track_llm_call(trace_name: Optional[str] = None):
    """Decorator to automatically track LLM calls"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracking = get_tracking()
            if not tracking:
                return func(*args, **kwargs)

            name = trace_name or f"{func.__module__}.{func.__name__}"

            with trace(name) as t:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    # Track error but don't interfere with exception flow
                    pass
                    raise

        return wrapper

    return decorator


# Simple function-based API for quick usage
def start_trace(name: str, **kwargs) -> Optional[str]:
    """Start a trace and return its ID"""
    tracking = get_tracking()
    if not tracking:
        return None

    trace_id = _generate_id()
    tracking.track(
        TrackingEvent(
            event_type="trace_start",
            trace_id=trace_id,
            timestamp=time.time(),
            data={"name": name, **kwargs},
        )
    )
    return trace_id


def end_trace(trace_id: str, output: Any = None):
    """End a trace"""
    tracking = get_tracking()
    if not tracking:
        return

    tracking.track(
        TrackingEvent(
            event_type="trace_end",
            trace_id=trace_id,
            timestamp=time.time(),
            data={"output": output},
        )
    )


def start_generation(trace_id: str, name: str, model: str, **kwargs) -> Optional[str]:
    """Start a generation and return its ID"""
    tracking = get_tracking()
    if not tracking:
        return None

    generation_id = _generate_id()
    tracking.track(
        TrackingEvent(
            event_type="generation_start",
            trace_id=trace_id,
            generation_id=generation_id,
            timestamp=time.time(),
            data={"name": name, "model": model, **kwargs},
        )
    )
    return generation_id


def end_generation(
    trace_id: str,
    generation_id: str,
    output: Any = None,
    usage: Optional[Dict[str, Any]] = None,
):
    """End a generation"""
    tracking = get_tracking()
    if not tracking:
        return

    tracking.track(
        TrackingEvent(
            event_type="generation_end",
            trace_id=trace_id,
            generation_id=generation_id,
            timestamp=time.time(),
            data={"output": output, "usage": usage},
        )
    )
