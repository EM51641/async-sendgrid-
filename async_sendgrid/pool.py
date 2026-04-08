"""
Connection pool manager for SendGrid API requests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from httpx import AsyncClient, Limits  # type: ignore
from httpx_retries import Retry, RetryTransport  # type: ignore

if TYPE_CHECKING:
    from typing import Any


class ConnectionPool:
    """
    A connection pool manager for SendGrid API requests.
    This is a private class and is not meant to be used directly.
    """

    def __init__(
        self,
        max_connections: int = 10,
        max_keepalive_connections: int = 5,
        keepalive_expiry: float = 5.0,
        total: int = 5,
        backoff_factor: float = 0.5,
    ) -> None:
        """
        Initialize the connection pool.

        Args:
            max_connections (int, optional):
                Maximum number of concurrent connections.
                Defaults to 10.
            max_keepalive_connections (int, optional):
                Maximum number of keep-alive connections.
                Defaults to 5.
            keepalive_expiry (float, optional):
                Keep-alive connection expiry time in
                seconds. Defaults to 5.0.
            total (int, optional):
                Maximum number of retry attempts for
                transient failures (429, 5xx, timeouts).
                Defaults to 5.
            backoff_factor (float, optional):
                Multiplier for exponential backoff between
                retries. Defaults to 0.5.
        """
        if not isinstance(total, int) or total < 0:
            raise ValueError(
                "total must be a positive integer"
            )
        if (
            not isinstance(backoff_factor, (int, float))
            or backoff_factor < 0
        ):
            raise ValueError(
                "backoff_factor must be a positive number"
            )

        self._limits = Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )
        self._retry = Retry(
            total=total,
            backoff_factor=backoff_factor,
        )
        self._client: AsyncClient | None = None

    def _create_client(self, headers: dict[str, Any]) -> AsyncClient:
        """
        Get or create an HTTP client with the configured connection limits.

        Args:
            headers (dict[str, Any]): The headers to use for the client.

        Returns:
            AsyncClient: The configured HTTP client.
        """
        transport = RetryTransport(retry=self._retry)
        return AsyncClient(
            headers=headers,
            limits=self._limits,
            timeout=5.0,
            transport=transport,
        )

    @property
    def limits(self) -> Limits:
        """
        Get the current connection limits.

        Returns:
            Limits: The current connection limits configuration.
        """
        return self._limits

    def __str__(self) -> str:
        return (
            f"ConnectionPool(max_connections={self._limits.max_connections}, "
            f"max_keepalive={self._limits.max_keepalive_connections}, "
            f"keepalive_expiry={self._limits.keepalive_expiry})"
        )
