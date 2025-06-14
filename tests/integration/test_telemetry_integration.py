import os
from typing import Generator

import pytest
from httpx import request
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from sendgrid.helpers.mail import Mail  # type: ignore

from async_sendgrid.sendgrid import SendgridAPI


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
def client() -> Generator[SendgridAPI, None, None]:
    """Setup client"""
    secret_key = os.environ["SENDGRID_API_KEY"]
    impersonate_subuser = "John Smith"
    endpoint = "http://localhost:3000/v3/mail/send"
    client = SendgridAPI(
        api_key=secret_key,
        endpoint=endpoint,
        impersonate_subuser=impersonate_subuser,
    )

    yield client

    request("DELETE", url="http://localhost:3000/api/mails")


@pytest.fixture
def email() -> Mail:
    email = Mail(
        from_email="johndoe@example.com",
        to_emails=["mahndoe@example.com"],
        subject="subject",
        plain_text_content="content",
    )
    return email


@pytest.mark.asyncio
async def test_successful_send_telemetry(
    exporter: InMemorySpanExporter, client: SendgridAPI, email: Mail
):

    await client.send(email)

    # Get the exported spans
    spans = exporter.get_finished_spans()

    assert len(spans) == 1
    span = spans[0]

    assert span.name == "sendgrid.send"
    assert span.attributes["http.url"] == "http://localhost:3000/v3/mail/send"  # type: ignore
    assert span.attributes["http.method"] == "POST"  # type: ignore
    assert span.attributes["http.status_code"] == 202  # type: ignore

    assert span.attributes["email.has_attachments"] is False  # type: ignore
    assert span.attributes["email.num_recipients"] == 1  # type: ignore

    assert span.status.is_ok == True


@pytest.mark.asyncio
async def test_stack_trace_is_recorded(
    exporter: InMemorySpanExporter, client: SendgridAPI, email: Mail
):
    await client.session.aclose()
    with pytest.raises(Exception):
        await client.send(email)
    # Get the exported spans
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]

    assert span.name == "sendgrid.send"
    assert span.attributes["email.has_attachments"] is False  # type: ignore
    assert span.attributes["email.num_recipients"] == 1  # type: ignore
    assert span.status.description.startswith("Session not initialized")  # type: ignore
    assert span.status.is_ok == False
