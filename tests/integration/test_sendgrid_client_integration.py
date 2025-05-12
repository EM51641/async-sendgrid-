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


@pytest.fixture
def messages_received():
    response = request("GET", url="http://localhost:3000/api/mails")
    return response.json()


@pytest.mark.asyncio
async def test_post_status(client: SendgridAPI, email: Mail) -> None:
    """
    Test the status code of the POST request.

    Args:
        email (Mail): The email object to be sent.
    Returns:
        None
    Raises:
        AssertionError: If the response status code is not 202.
    """
    async with client:
        response = await client.send(email)

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_session_closed_exception(
    client: SendgridAPI, email: Mail
) -> None:
    """
    Test that the SessionClosedException is raised when the session is closed.
    """
    async with client:
        assert client.session
        await client.session.aclose()
        assert client.session.is_closed
        with pytest.raises(SessionClosedException):
            await client.send(email)


@pytest.mark.asyncio
async def test_if_messages_sent_are_correct(
    client: SendgridAPI, email: Mail
) -> None:
    """
    Test if the sent messages are valid.
    Args:
        email (Mail): The email message to be sent.
    Returns:
        None
    """
    async with client:
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
