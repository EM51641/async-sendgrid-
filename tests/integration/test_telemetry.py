import os
from typing import Generator

import pytest
from httpx import request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from sendgrid.helpers.mail import Mail

from async_sendgrid.sendgrid import SendgridAPI


@pytest.fixture
def exporter() -> InMemorySpanExporter:
    return InMemorySpanExporter()


@pytest.fixture
def tracer_provider(exporter: InMemorySpanExporter) -> TracerProvider:
    """Create a new tracer provider for testing"""
    provider = TracerProvider()
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    return provider


@pytest.fixture
def client(
    tracer_provider: TracerProvider,
) -> Generator[SendgridAPI, None, None]:
    """Setup client"""
    # Set the tracer provider before creating the client

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
        to_emails="mahndoe@example.com",
        subject="Example email",
        plain_text_content="Hello World!",
    )
    return email


@pytest.mark.asyncio
async def test_successful_send_telemetry(
    exporter: InMemorySpanExporter,
    client: SendgridAPI,
    email: Mail,
    tracer_provider: TracerProvider,
):
    trace.set_tracer_provider(tracer_provider)

    response = await client.send(email)

    # Get the exported spans
    spans = exporter.get_finished_spans()

    assert len(spans) == 1
    span = spans[0]
    assert span.name == "sendgrid.send"
