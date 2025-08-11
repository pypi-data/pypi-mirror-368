import time
from unittest.mock import Mock, patch

import pytest
from kairoz.tracking import (
    GenerationContext,
    KairozTracking,
    SpanContext,
    TraceContext,
    TrackingEvent,
    add_score,
    end_generation,
    end_trace,
    get_tracking,
    initialize_tracking,
    start_generation,
    start_trace,
    trace,
    track_llm_call,
)


class TestKairozTracking:
    """Test cases for KairozTracking class"""

    def setup_method(self):
        """Setup for each test method"""
        self.mock_session = Mock()
        self.mock_session.post = Mock()
        self.mock_session.headers = Mock()
        self.mock_session.headers.update = Mock()

    @patch("requests.Session")
    def test_initialization(self, mock_session_class):
        """Test KairozTracking initialization"""
        mock_session_class.return_value = self.mock_session

        tracking = KairozTracking(api_key="test-key")

        assert tracking.api_key == "test-key"
        assert tracking.base_url == "https://api.kairozai.com"
        assert tracking.max_queue_size == 1000

        # Check session headers
        self.mock_session.headers.update.assert_called_with(
            {"Authorization": "Bearer test-key"}
        )

    @patch("requests.Session")
    def test_initialization_with_custom_base_url(self, mock_session_class):
        """Test initialization with custom base URL"""
        mock_session_class.return_value = self.mock_session

        tracking = KairozTracking(
            api_key="test-key", base_url="https://custom.kairozai.com"
        )

        assert tracking.base_url == "https://custom.kairozai.com"

    @patch("requests.Session")
    def test_track_event(self, mock_session_class):
        """Test tracking an event"""
        mock_session_class.return_value = self.mock_session

        tracking = KairozTracking(api_key="test-key")

        event = TrackingEvent(
            event_type="trace_start",
            trace_id="test-trace-id",
            timestamp=time.time(),
            data={"name": "test-trace"},
        )

        # Should not raise exception
        tracking.track(event)

        # Event should be in queue
        assert not tracking.event_queue.empty()

    @patch("requests.Session")
    def test_track_event_when_offline(self, mock_session_class):
        """Test tracking when offline"""
        mock_session_class.return_value = self.mock_session

        tracking = KairozTracking(api_key="test-key")
        tracking.is_online = False

        event = TrackingEvent(
            event_type="trace_start",
            trace_id="test-trace-id",
            timestamp=time.time(),
            data={"name": "test-trace"},
        )

        tracking.track(event)

        # Queue should be empty when offline
        assert tracking.event_queue.empty()

    @patch("requests.Session")
    def test_flush(self, mock_session_class):
        """Test manual flush"""
        mock_session_class.return_value = self.mock_session
        self.mock_session.post.return_value.raise_for_status = Mock()

        tracking = KairozTracking(api_key="test-key")

        event = TrackingEvent(
            event_type="trace_start",
            trace_id="test-trace-id",
            timestamp=time.time(),
            data={"name": "test-trace"},
        )

        tracking.track(event)
        tracking.flush()

        # Should have called the API
        self.mock_session.post.assert_called()


class TestTrackingEvent:
    """Test cases for TrackingEvent"""

    def test_event_creation(self):
        """Test creating a tracking event"""
        timestamp = time.time()
        event = TrackingEvent(
            event_type="trace_start",
            trace_id="test-trace-id",
            timestamp=timestamp,
            data={"name": "test-trace"},
        )

        assert event.type == "trace_start"
        assert event.trace_id == "test-trace-id"
        assert event.timestamp == timestamp
        assert event.data == {"name": "test-trace"}

    def test_event_to_dict(self):
        """Test converting event to dictionary"""
        timestamp = time.time()
        event = TrackingEvent(
            event_type="trace_start",
            trace_id="test-trace-id",
            timestamp=timestamp,
            data={"name": "test-trace"},
            generation_id="gen-id",
        )

        result = event.to_dict()

        assert result["type"] == "trace_start"
        assert result["traceId"] == "test-trace-id"
        assert result["timestamp"] == int(timestamp * 1000)
        assert result["data"] == {"name": "test-trace"}
        assert result["generationId"] == "gen-id"


class TestGlobalFunctions:
    """Test cases for global tracking functions"""

    def setup_method(self):
        """Setup for each test method"""
        # Clear any existing global tracking
        import kairoz.tracking

        kairoz.tracking._global_tracking = None

    def test_initialize_tracking(self):
        """Test initializing global tracking"""
        with patch("requests.Session"):
            tracking = initialize_tracking(api_key="test-key")
            assert tracking is not None
            assert get_tracking() is tracking

    def test_get_tracking_when_not_initialized(self):
        """Test getting tracking when not initialized"""
        assert get_tracking() is None

    @patch("kairoz.tracking.get_tracking")
    def test_start_trace_without_initialization(self, mock_get_tracking):
        """Test starting trace without initialization"""
        mock_get_tracking.return_value = None

        trace_id = start_trace("test-trace")
        assert trace_id is None

    def test_add_score_without_initialization(self):
        """Test adding score without initialization"""
        # Should not raise exception
        add_score("test-score", 0.8)


class TestContextManagers:
    """Test cases for context managers"""

    def setup_method(self):
        """Setup for each test method"""
        # Clear any existing global tracking
        import kairoz.tracking

        kairoz.tracking._global_tracking = None

    @patch("requests.Session")
    def test_trace_context_manager(self, mock_session_class):
        """Test trace context manager"""
        mock_session_class.return_value = Mock()
        initialize_tracking(api_key="test-key")

        with trace("test-trace", user_id="user-123") as t:
            assert isinstance(t, TraceContext)

    @patch("requests.Session")
    def test_generation_context_manager(self, mock_session_class):
        """Test generation context manager"""
        mock_session_class.return_value = Mock()
        initialize_tracking(api_key="test-key")

        with trace("test-trace") as t:
            with t.generation("test-gen", "gpt-4") as gen:
                assert isinstance(gen, GenerationContext)
                gen.update(
                    output="Test response",
                    usage={"promptTokens": 10, "completionTokens": 5},
                )

    @patch("requests.Session")
    def test_span_context_manager(self, mock_session_class):
        """Test span context manager"""
        mock_session_class.return_value = Mock()
        initialize_tracking(api_key="test-key")

        with trace("test-trace") as t:
            with t.span("test-span") as span:
                assert isinstance(span, SpanContext)
                span.update(output={"result": "success"})

    def test_trace_context_without_tracking(self):
        """Test trace context when tracking not initialized"""
        # Should not raise exception and return stub
        with trace("test-trace") as t:
            # Should be a stub that doesn't raise errors
            with t.generation("test-gen", "gpt-4") as gen:
                gen.update(output="test")
            with t.span("test-span") as span:
                span.update(output="test")


class TestDecorator:
    """Test cases for track_llm_call decorator"""

    def setup_method(self):
        """Setup for each test method"""
        # Clear any existing global tracking
        import kairoz.tracking

        kairoz.tracking._global_tracking = None

    @patch("requests.Session")
    def test_decorator_with_tracking(self, mock_session_class):
        """Test decorator when tracking is initialized"""
        mock_session_class.return_value = Mock()
        initialize_tracking(api_key="test-key")

        @track_llm_call("test-function")
        def test_function(message: str) -> str:
            return f"Response to: {message}"

        result = test_function("Hello")
        assert result == "Response to: Hello"

    def test_decorator_without_tracking(self):
        """Test decorator when tracking is not initialized"""

        @track_llm_call("test-function")
        def test_function(message: str) -> str:
            return f"Response to: {message}"

        result = test_function("Hello")
        assert result == "Response to: Hello"

    @patch("requests.Session")
    def test_decorator_with_exception(self, mock_session_class):
        """Test decorator handles exceptions properly"""
        mock_session_class.return_value = Mock()
        initialize_tracking(api_key="test-key")

        @track_llm_call("failing-function")
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()


class TestComplexScenarios:
    """Test cases for complex tracking scenarios"""

    def setup_method(self):
        """Setup for each test method"""
        # Clear any existing global tracking
        import kairoz.tracking

        kairoz.tracking._global_tracking = None

    @patch("requests.Session")
    def test_nested_contexts(self, mock_session_class):
        """Test nested trace, generation, and span contexts"""
        mock_session_class.return_value = Mock()
        initialize_tracking(api_key="test-key")

        with trace("rag-pipeline", user_id="user-123") as t:
            # Document retrieval span
            with t.span("document-retrieval") as retrieval_span:
                retrieval_span.update(output={"documents": ["doc1", "doc2"]})

            # LLM generation
            with t.generation("answer-generation", "gpt-4") as gen:
                gen.update(
                    output="Generated answer",
                    usage={
                        "promptTokens": 100,
                        "completionTokens": 50,
                        "totalTokens": 150,
                    },
                )

            # Add score
            add_score("relevance", 0.85, comment="High relevance")

    @patch("requests.Session")
    def test_multiple_parallel_traces(self, mock_session_class):
        """Test multiple traces running in parallel"""
        mock_session_class.return_value = Mock()
        initialize_tracking(api_key="test-key")

        # Start multiple traces
        trace_id_1 = start_trace("trace-1")
        trace_id_2 = start_trace("trace-2")

        # Start generations in each trace
        gen_id_1 = start_generation(trace_id_1, "gen-1", "gpt-4")
        gen_id_2 = start_generation(trace_id_2, "gen-2", "gpt-3.5-turbo")

        # End generations
        end_generation(trace_id_1, gen_id_1, output="Response 1")
        end_generation(trace_id_2, gen_id_2, output="Response 2")

        # End traces
        end_trace(trace_id_1, output={"success": True})
        end_trace(trace_id_2, output={"success": True})

    @patch("requests.Session")
    def test_error_handling_in_context(self, mock_session_class):
        """Test error handling within trace context"""
        mock_session_class.return_value = Mock()
        initialize_tracking(api_key="test-key")

        try:
            with trace("error-test") as t:
                with t.generation("failing-gen", "gpt-4") as gen:
                    # Simulate error
                    raise RuntimeError("Simulated error")
        except RuntimeError:
            pass  # Expected error

        # Should complete without additional errors
        assert True
