"""
Connection pool manager for SendGrid API requests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from httpx import AsyncClient, Limits  # type: ignore

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
    ) -> None:
        """
        Initialize the connection pool.

        Args:
            max_connections (int, optional):
                Maximum number of concurrent connections. Defaults to 10.
            max_keepalive_connections (int, optional):
                Maximum number of keep-alive connections. Defaults to 5.
            keepalive_expiry (float, optional):
                Keep-alive connection expiry time in seconds. Defaults to 5.0.
        """
        self._limits = Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
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
        return AsyncClient(headers=headers, limits=self._limits, timeout=5.0)

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
