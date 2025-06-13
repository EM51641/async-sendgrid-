from typing import Any, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace.span import Span

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer = tracer_provider.get_tracer(__name__)


def create_span(
    name: str, attributes: Optional[dict[str, Any]] = None
) -> Span:
    """Create a new OpenTelemetry span"""
    return tracer.start_span(name, attributes=attributes)
