import logging
import os

import pytest
import pytest_asyncio
from httpx import request
from sendgrid import Mail  # type: ignore

from async_sendgrid.exception import SessionClosedException
from async_sendgrid.pool import ConnectionPool
from async_sendgrid.sendgrid import SendgridAPI


@pytest_asyncio.fixture
async def client():
    """Setup client with its own pool to avoid shared mutable state."""
    secret_key = os.environ["SENDGRID_API_KEY"]
    on_behalf_of = "John Smith"
    endpoint = "http://localhost:3000/v3/mail/send"
    pool = ConnectionPool()
    client = SendgridAPI(
        api_key=secret_key,
        endpoint=endpoint,
        on_behalf_of=on_behalf_of,
        pool=pool,
    )
    yield client
    await pool.shutdown()


@pytest.mark.asyncio
async def test_post_status(client: SendgridAPI) -> None:
    """
    Test the status code of the POST request.

    Args:
        email (Mail): The email object to be sent.
    Returns:
        None
    Raises:
        AssertionError: If the response status code is not 202.
    """
    response = await client.send(
        Mail(
            from_email="johndoe@example.com",
            to_emails="mahndoe@example.com",
            subject="Example email",
            plain_text_content="Hello World!",
        )
    )
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_if_messages_sent_are_correct(client: SendgridAPI) -> None:
    """
    Test if the sent messages are valid.
    Args:
        email (Mail): The email message to be sent.
    Returns:
        None
    """
    email = Mail(
        from_email="johndoe@example.com",
        to_emails="mahndoe@example.com",
        subject="Example email",
        plain_text_content="Hello World!",
    )

    await client.send(email)

    response = request("GET", url="http://localhost:3000/api/mails")
    messages = response.json()

    assert len(messages) == 1

    msg = messages[0]

    assert msg["from"] == {"email": "johndoe@example.com"}
    assert msg["subject"] == "Example email"
    assert msg["personalizations"] == [
        {"to": [{"email": "mahndoe@example.com"}]}
    ]
    assert msg["content"] == [{"type": "text/plain", "value": "Hello World!"}]


@pytest.mark.asyncio
async def test_session_rebuilds_after_unexpected_close(
    client: SendgridAPI, caplog: pytest.LogCaptureFixture
):
    """
    Test that closing the session without shutting down the pool
    transparently rebuilds the client.
    """
    await client.session.aclose()

    with caplog.at_level(logging.DEBUG, logger="async_sendgrid.sendgrid"):
        response = await client.send(
            Mail(
                from_email="johndoe@example.com",
                to_emails="mahndoe@example.com",
                subject="Rebuild test",
                plain_text_content="Hello!",
            )
        )

    assert response.status_code == 202
    assert any(
        "rebuilding client" in record.message for record in caplog.records
    )


@pytest.mark.asyncio
async def test_session_raises_after_explicit_shutdown(
    client: SendgridAPI, caplog: pytest.LogCaptureFixture
):
    """
    Test that calling pool.shutdown() and then sending raises
    SessionClosedException.
    """
    await client.pool.shutdown()

    with pytest.raises(SessionClosedException):
        await client.send(Mail())

    assert caplog.record_tuples == [
        (
            "async_sendgrid.sendgrid",
            logging.ERROR,
            "Session not initialized",
        )
    ]
