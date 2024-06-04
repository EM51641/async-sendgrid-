from unittest.mock import patch

import pytest

from async_sendgrid.sendgrid import SendgridAPI


class TestAsyncClient:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        secret_key = "SECRET_KEY"
        impersonate_subuser = "John Smith"
        self._service = SendgridAPI(
            api_key=secret_key, impersonate_subuser=impersonate_subuser
        )

    def test_constructor(self) -> None:
        """
        Test constructor.
        """
        assert (
            self._service.endpoint == "https://api.sendgrid.com/v3/mail/send"
        )
        assert self._service.api_key == "SECRET_KEY"
        assert self._service.headers == {
            "Authorization": "Bearer SECRET_KEY",
            "User-Agent": "async_sendgrid;python",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "On-Behalf-Of": "John Smith",
        }
