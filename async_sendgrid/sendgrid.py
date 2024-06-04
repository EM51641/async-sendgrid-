from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from httpx import AsyncClient  # type: ignore

from async_sendgrid.utils import create_session

if TYPE_CHECKING:
    from typing import Any, Optional

    from httpx import Response  # type: ignore
    from sendgrid.helpers.mail import Mail  # type: ignore


class BaseSendgridAPI(ABC):
    @property
    @abstractmethod
    def api_key(self) -> str:
        """Not implemented"""

    @property
    @abstractmethod
    def endpoint(self) -> str:
        """Not implemented"""

    @property
    @abstractmethod
    def headers(self) -> dict[Any, Any]:
        """Not implemented"""

    @abstractmethod
    async def send(self, message: Mail) -> Response:
        """Not implemented"""


class SendgridAPI(BaseSendgridAPI):
    """
    Construct the Twilio SendGrid v3 API object.
    Note that the underlying client is being Setup during initialization,
    therefore changing attributes in runtime will not affect HTTP client
    behaviour.

    :param api_key: The api key issued by Sendgrid.
    :param endpoint: The endpoint to send the request to. Defaults to
        "https://api.sendgrid.com/v3/mail/send".
    :param impersonate_subuser: the subuser to impersonate. Will be passed
        by "On-Behalf-Of" header by underlying client.
        See https://sendgrid.com/docs/User_Guide/Settings/subusers.html
        for more details.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://api.sendgrid.com/v3/mail/send",
        impersonate_subuser: Optional[str] = None,
    ):
        self._api_key = api_key
        self._endpoint = endpoint

        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": "sendgrid-async;python",
            "Accept": "*/*",
            "Content-Type": "application/json",
        }

        if impersonate_subuser:
            self._headers["On-Behalf-Of"] = impersonate_subuser

        self._session: AsyncClient | None = None

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def headers(self) -> dict[Any, Any]:
        return self._headers

    async def send(self, message: Mail) -> Response:
        """
        Make a Twilio SendGrid v3 API request with the request body generated
        by the Mail object

        Parameters:
        ----
            :param message: The Twilio SendGrid v3 API request body generated
                by the Mail object or dict
        Returns:
        ----
            :return: The Twilio SendGrid v3 API response
        """
        assert self._session

        json_message = message.get()
        response = await self._session.post(
            url=self._endpoint, json=json_message
        )
        return response

    async def __aenter__(self):
        if not self._session or self._session.is_closed:
            self._session = create_session(headers=self._headers)
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any):
        assert self._session

        await self._session.aclose()
