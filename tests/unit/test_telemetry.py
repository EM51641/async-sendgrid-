import os
from unittest.mock import Mock

import pytest
from httpx import URL, Request, Response
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace.span import Span
from sendgrid.helpers.mail import Attachment, Mail  # type: ignore

import async_sendgrid.telemetry
from async_sendgrid.sendgrid import SendgridAPI
from async_sendgrid.telemetry import (
    create_span,
    set_http_metrics,
    set_sendgrid_metrics,
    trace_client,
)


@pytest.fixture
def exporter() -> InMemorySpanExporter:
    return InMemorySpanExporter()


@pytest.fixture(autouse=True)
def tracer_config(
    provider: TracerProvider, exporter: InMemorySpanExporter
) -> None:
    """Create a new tracer provider for testing"""
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)


@pytest.fixture
def span() -> Span:
    tracer = trace.get_tracer(__name__)
    return tracer.start_span(__name__)


def test_create_span():
    span = create_span("test")
    assert span.name == "test"


@pytest.mark.parametrize(
    "attachments, expected",
    [
        ([], False),
        ([Attachment(file_type="text/plain")], True),
    ],
)
def test_set_sendgrid_metrics_attachments(
    attachments: list[Attachment],
    expected: bool,
    span: Span,
):
    email = Mail()
    for attachment in attachments:
        email.add_attachment(attachment)
    set_sendgrid_metrics(span, email)
    assert span.attributes["email.has_attachments"] == expected  # type: ignore


@pytest.mark.parametrize(
    "recipients, expected",
    [
        (["test@example.com"], 1),
        (["test1@example.com", "test2@example.com"], 2),
    ],
)
def test_set_sendgrid_metrics_recipients(
    recipients: list[str], expected: int, span: Span
):
    email = Mail(
        from_email="test@example.com",
        to_emails=recipients,
        subject="test",
        html_content="test",
    )
    set_sendgrid_metrics(span, email)
    assert span.attributes["email.num_recipients"] == expected  # type: ignore


@pytest.mark.parametrize(
    "status_code, expected_status",
    [
        (200, True),
        (400, False),
    ],
)
def test_set_http_metrics_status_code(
    status_code: int,
    expected_status: bool,
    span: Span,
):
    response = Response(status_code=status_code, content=b"test")
    response.request = Request(method="GET", url=URL("https://example.com"))

    set_http_metrics(span, response)

    assert span.attributes["http.status_code"] == status_code  # type: ignore
    assert span.status.is_ok == expected_status  # type: ignore


@pytest.mark.parametrize(
    "content, expected_length",
    [
        ("content", 7),
        ("error", 5),
    ],
)
def test_set_http_metrics_content(
    content: str,
    expected_length: int,
    span: Span,
):
    response = Response(status_code=200, content=content.encode())
    response.request = Request(method="GET", url=URL("https://example.com"))

    set_http_metrics(span, response)

    assert span.attributes["http.content_length"] == expected_length  # type: ignore


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://example.fr",
    ],
)
def test_set_http_metrics_url(
    url: str,
    span: Span,
):
    response = Response(status_code=200, content=b"test")
    response.request = Request(method="GET", url=URL(url))

    set_http_metrics(span, response)

    assert span.attributes["http.url"] == url  # type: ignore


@pytest.mark.parametrize(
    "method",
    [
        "GET",
        "POST",
    ],
)
def test_set_http_metrics_method(
    method: str,
    span: Span,
):
    response = Response(status_code=200, content=b"test")
    response.request = Request(method=method, url=URL("https://example.com"))

    set_http_metrics(span, response)

    assert span.attributes["http.method"] == method  # type: ignore
