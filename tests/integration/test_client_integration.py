import pytest
from httpx import request
from sendgrid import Mail

from async_sendgrid.sendgrid import SendgridAPI


class TestClient:

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup client"""
        secret_key = "SG.test123"
        impersonate_subuser = "John Smith"
        self._service = SendgridAPI(
            api_key=secret_key, impersonate_subuser=impersonate_subuser
        )
        yield

    @pytest.mark.asyncio
    async def test_send(self) -> None:
        """
        Test post response.
        """
        email = Mail(
            from_email="johndoe@example.com",
            to_emails="mahndoe@example.com",
            subject="Example email",
            plain_text_content="Hello",
        )

        async with self._service as client:
            response = await client.send(email)

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_get_message(self) -> None:

        email = Mail(
            from_email="johndoe@example.com",
            to_emails="mahndoe@example.com",
            subject="Example email",
            plain_text_content="Hello",
        )

        async with self._service as client:
            await client.send(email)

        messages = request("GET", url="/api/mails")

        assert len(messages) == 1
        msg = messages[0]

        assert msg["To"] == "mahndoe@example.com"
