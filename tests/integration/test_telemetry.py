import base64
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
from sendgrid.helpers.mail import Attachment, FileContent, Mail  # type: ignore

from async_sendgrid.sendgrid import SendgridAPI


@pytest.fixture(scope="session")
def provider() -> Generator[TracerProvider, None, None]:
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    yield provider
    provider.shutdown()


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
        to_emails=["mahndoe@example.com", "mahndoe2@example.com"],
        subject="subject",
        plain_text_content="content",
    )

    with open(
        "tests/integration/attachements/test_attachement.txt", "rb"
    ) as file:
        file_content = file.read()

    encoded_file_content = base64.b64encode(file_content).decode("utf-8")

    email.add_attachment(
        Attachment(
            file_content=FileContent(encoded_file_content),
            file_name="test_attachement.txt",
            file_type="text/plain",
        )
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

    assert span.attributes["email.has_attachments"] is True  # type: ignore
    assert span.attributes["email.num_recipients"] == 2  # type: ignore

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
    assert span.attributes["email.has_attachments"] is True  # type: ignore
    assert span.attributes["email.num_recipients"] == 2  # type: ignore
    assert span.status.description.startswith("Session not initialized")  # type: ignore
    assert span.status.is_ok == False
