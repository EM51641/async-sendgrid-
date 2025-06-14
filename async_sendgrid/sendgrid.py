"""
Sendgrid API client.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from httpx import AsyncClient  # type: ignore

from async_sendgrid.exception import SessionClosedException
from async_sendgrid.pool import ConnectionPool
from async_sendgrid.telemetry import trace_client

logger = logging.getLogger(__name__)

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

    @property
    @abstractmethod
    def session(self) -> AsyncClient | None:
        """Not implemented"""

    @property
    @abstractmethod
    def pool(self) -> ConnectionPool:
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
    :param on_behalf_of: The subuser to send on behalf of. This will be passed
        as the "On-Behalf-Of" header in API requests.
        See https://sendgrid.com/docs/User_Guide/Settings/subusers.html
        for more details.
    :param pool:
        The connection pool to use. Defaults to a new ConnectionPool instance.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://api.sendgrid.com/v3/mail/send",
        on_behalf_of: Optional[str] = None,
        pool: ConnectionPool = ConnectionPool(),
    ):
        self._api_key = api_key
        self._endpoint = endpoint

        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": "sendgrid-async;python",
            "Accept": "*/*",
            "Content-Type": "application/json",
        }

        if on_behalf_of:
            self._headers["On-Behalf-Of"] = on_behalf_of

        self._pool = pool
        self._session = self._pool._create_client(self._headers)

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def headers(self) -> dict[Any, Any]:
        return self._headers

    @property
    def pool(self) -> ConnectionPool:
        return self._pool

    @property
    def session(self) -> AsyncClient:
        return self._session

    @trace_client()
    async def send(self, email: Mail) -> Response:
        """
        Make a Twilio SendGrid v3 API request with the request body generated
        by the Mail object

        Args:
            email: The Twilio SendGrid v3 API request body generated
                by the Mail object or dict

        Returns:
            The Twilio SendGrid v3 API response
        """
        self._check_session_closed()
        json_message = email.get()
        response = await self._session.post(
            url=self._endpoint, json=json_message
        )
        return response

    def _check_session_closed(self):
        """
        Check if the session is closed.

        Raises:
            SessionClosedException: If the session is closed.
        """
        if self._session.is_closed:
            logger.error("Session not initialized")
            raise SessionClosedException("Session not initialized")

    def __str__(self) -> str:
        return f"SendGrid API Client\n  • Endpoint: {self._endpoint}\n"

    def __repr__(self) -> str:
        return f"SendgridAPI(endpoint={self._endpoint})"
