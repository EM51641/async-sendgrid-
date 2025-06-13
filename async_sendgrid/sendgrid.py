from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from httpx import AsyncClient  # type: ignore
from opentelemetry.trace.span import Span
from opentelemetry.trace.status import StatusCode

from async_sendgrid.exception import SessionClosedException
from async_sendgrid.pool import ConnectionPool
from async_sendgrid.telemetry import create_span

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

        if impersonate_subuser:
            self._headers["On-Behalf-Of"] = impersonate_subuser

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
        with _create_sendgrid_client_span(message, self._endpoint) as span:
            self._check_session_closed(span)

            json_message = message.get()
            response = await self._session.post(
                url=self._endpoint, json=json_message
            )
            self._set_response_metrics(span, response)
            return response

    def _check_session_closed(self, span: Span):
        if self._session.is_closed:
            span.set_attributes(
                {
                    "error.message": "Session not initialized",
                    "error.type": "SessionClosedException",
                }
            )
            span.set_status(
                StatusCode.ERROR,
                "Session not initialized",
            )
            raise SessionClosedException("Session not initialized")

    def _set_response_metrics(self, span: Span, response: Response):
        span.set_attributes(
            {
                "http.status_code": response.status_code,
                "http.content_length": (
                    len(response.content) if response.content else 0
                ),
            }
        )

        if response.status_code >= 400:
            span.set_status(
                StatusCode.ERROR,
                f"Request failed with status code {response.status_code}",
            )

    def __str__(self) -> str:
        return f"SendGrid API Client\n  • Endpoint: {self._endpoint}\n"

    def __repr__(self) -> str:
        return f"SendgridAPI(endpoint={self._endpoint})"


def _create_sendgrid_client_span(message: Mail, endpoint: str) -> Span:
    """
    Create a span for tracking SendGrid API requests.

    This function creates a span with metrics about the SendGrid email being sent,
    including:
    - The endpoint being used
    - Size of the message
    - Whether the message has attachments
    - Content types in the message
    - Number of recipients

    Parameters:
    ----
        :param message: The SendGrid Mail object containing the email details

    Returns:
    ----
        :return: A span object for tracking the API request
    """
    return create_span(
        "sendgrid.send",
        {
            "http.url": endpoint,
            "http.message_size": len(str(message.get())),
            "http.has_attachments": bool(message.attachment),
            "http.content_types": [c.type for c in message.content or []],
            "http.num_recipients": (
                len(message.personalizations[0].tos)
                if message.personalizations
                else 0
            ),
        },
    )
