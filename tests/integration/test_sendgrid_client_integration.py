import logging
import os

import pytest
from httpx import request
from sendgrid import Mail  # type: ignore

from async_sendgrid.exception import SessionClosedException
from async_sendgrid.sendgrid import SendgridAPI


@pytest.fixture
def client():
    """Setup client"""
    secret_key = os.environ["SENDGRID_API_KEY"]
    on_behalf_of = "John Smith"
    endpoint = "http://localhost:3000/v3/mail/send"
    client = SendgridAPI(
        api_key=secret_key,
        endpoint=endpoint,
        on_behalf_of=on_behalf_of,
    )

    yield client

    request("DELETE", url="http://localhost:3000/api/mails")


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
async def test_if_session_is_closed_raises_exception(
    client: SendgridAPI, caplog: pytest.LogCaptureFixture
):
    """
    Test if the session is closed raises an exception.
    """

    email = Mail()

    await client.session.aclose()

    with pytest.raises(SessionClosedException):
        await client.send(email)

    assert caplog.record_tuples == [
        (
            "async_sendgrid.sendgrid",
            logging.ERROR,
            "Session not initialized",
        )
    ]
