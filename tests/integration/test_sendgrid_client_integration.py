import pytest
from httpx import request
from sendgrid import Mail  # type: ignore

from async_sendgrid.sendgrid import SendgridAPI


class TestSendgridClient:

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup client"""
        secret_key = "SG.test123"
        impersonate_subuser = "John Smith"
        endpoint = "http://localhost:3000/v3/mail/send"
        self._service = SendgridAPI(
            api_key=secret_key,
            endpoint=endpoint,
            impersonate_subuser=impersonate_subuser,
        )

        yield

        request("DELETE", url="http://localhost:3000/api/mails")

    @pytest.fixture()
    def email(self) -> Mail:
        email = Mail(
            from_email="johndoe@example.com",
            to_emails="mahndoe@example.com",
            subject="Example email",
            plain_text_content="Hello World!",
        )
        return email

    @pytest.fixture
    def messages_received(self):
        response = request("GET", url="http://localhost:3000/api/mails")
        return response.json()

    @pytest.mark.asyncio
    async def test_post_status(self, email: Mail) -> None:
        """
        Test the status code of the POST request.

        Args:
            email (Mail): The email object to be sent.

        Returns:
            None

        Raises:
            AssertionError: If the response status code is not 202.
        """
        async with self._service as client:
            response = await client.send(email)

        assert response.status_code == 202

    @pytest.mark.asyncio
    async def test_if_messages_sent_are_correct(self, email: Mail) -> None:
        """
        Test if the sent messages are valid.

        Args:
            email (Mail): The email message to be sent.

        Returns:
            None
        """

        async with self._service as client:
            await client.send(email)

        response = request("GET", url="http://localhost:3000/api/mails")
        messages = response.json()

        assert len(messages) == 1
        msg = messages[0]

        assert msg["from"]["email"] == "johndoe@example.com"
        assert msg["subject"] == "Example email"

        assert len(msg["personalizations"]) == 1
        assert len(msg["personalizations"][0]["to"]) == 1
        assert (
            msg["personalizations"][0]["to"][0]["email"]
            == "mahndoe@example.com"
        )

        assert len(msg["content"]) == 1
        assert msg["content"][0]["value"] == "Hello World!"
        assert msg["content"][0]["type"] == "text/plain"
