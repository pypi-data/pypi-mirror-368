from .client import Kairoz
from .openai import KairozOpenAI, ProviderConfig
from .prompt import Prompt
from .providers import Providers
from .tracking import (
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
from .version import __version__

# Default instance
kairoz = Kairoz()

# Exports for direct imports
__all__ = [
    "Kairoz",
    "Prompt",
    "KairozOpenAI",
    "ProviderConfig",
    "Providers",
    "kairoz",
    "__version__",
    "KairozTracking",
    "TrackingEvent",
    "TraceContext",
    "GenerationContext",
    "SpanContext",
    "initialize_tracking",
    "get_tracking",
    "trace",
    "add_score",
    "track_llm_call",
    "start_trace",
    "end_trace",
    "start_generation",
    "end_generation",
]
