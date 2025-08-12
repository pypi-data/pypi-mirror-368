import os


def is_tracing_enabled() -> bool:
    return (os.getenv("IMPACT_TRACING_ENABLED") or "true").lower() == "true"


def is_content_tracing_enabled() -> bool:
    return (os.getenv("IMPACT_TRACE_CONTENT") or "true").lower() == "true"




