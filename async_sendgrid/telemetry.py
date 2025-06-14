from __future__ import annotations

import base64
from functools import wraps
from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace.span import Span
from opentelemetry.trace.status import Status, StatusCode

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Optional, TypeVar

    from httpx import Response  # type: ignore
    from sendgrid.helpers.mail import Mail  # type: ignore

    from async_sendgrid.sendgrid import SendgridAPI

    F = TypeVar("F", bound=Callable[..., Any])

# Only create a default tracer provider if one isn't already set
if trace.get_tracer_provider() is None:
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)


def create_span(
    name: str, attributes: Optional[dict[str, Any]] = None
) -> Span:
    """Create a new OpenTelemetry span"""
    tracer = trace.get_tracer(name)
    span = tracer.start_span(name, attributes=attributes)
    return span


def trace_response() -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(
            self: SendgridAPI, mail: Mail
        ) -> Response:  # Explicit parameter type
            span = create_span("sendgrid.send")
            try:
                _set_sendgrid_metrics(span, mail)
                response: Response = await func(self, mail)
                _set_http_metrics(span, response)
                return response
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
            finally:
                span.end()

        return wrapper  # type: ignore

    return decorator  # type: ignore


def _set_sendgrid_metrics(span: Span, message: Mail) -> None:
    """
    Set SendGrid metrics on a span.
    """
    span.set_attributes(
        {
            "email.has_attachments": True if message.attachments else False,
            "email.num_recipients": len(message.personalizations[0].tos),
        }
    )


def _set_http_metrics(span: Span, response: Response) -> None:
    """
    Set response metrics on a span.
    """
    span.set_attributes(
        {
            "http.status_code": response.status_code,
            "http.url": str(response.url),
            "http.content_length": (
                len(response.content) if response.content else 0
            ),
            "http.method": response.request.method,
        }
    )

    if response.status_code >= 400:
        span.set_status(
            StatusCode.ERROR, f"Request failed with message {response.text}"
        )
