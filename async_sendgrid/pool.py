"""
Connection pool manager for SendGrid API requests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from httpx import AsyncClient, AsyncHTTPTransport, Limits  # type: ignore
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
        retry_attempts: int = 5,
        backoff_factor: float = 0.5,
        backoff_jitter: float = 1.0,
        timeout: float = 5.0,
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
            retry_attempts (int, optional):
                Maximum number of retry attempts for
                transient failures (429, 5xx, timeouts).
                Defaults to 5.
            backoff_factor (float, optional):
                Multiplier for exponential backoff between
                retries. Defaults to 0.5.
            backoff_jitter (float, optional):
                Jitter multiplier applied to the backoff time,
                between 0 and 1. Defaults to 1.0.
            timeout (float, optional):
                Request timeout in seconds. Defaults to 5.0.
        """
        self._validate_retry_attempts(retry_attempts)
        self._validate_backoff_factor(backoff_factor)
        self._validate_backoff_jitter(backoff_jitter)
        self._validate_timeout(timeout)

        self._limits = Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )
        self._retry = Retry(
            total=retry_attempts,
            backoff_factor=backoff_factor,
            backoff_jitter=backoff_jitter,
            allowed_methods=["POST"],
        )
        self._timeout = timeout
        self._client: AsyncClient | None = None
        self._shutdown = False

    def _create_client(self, headers: dict[str, Any]) -> AsyncClient:
        """
        Get or create the long-lived HTTP client backed by the pool.

        Args:
            headers (dict[str, Any]): The headers to use for the client.

        Returns:
            AsyncClient: The configured HTTP client.
        """
        if self._client is not None and not self._client.is_closed:
            return self._client

        transport = RetryTransport(
            transport=AsyncHTTPTransport(limits=self._limits),
            retry=self._retry,
        )
        self._client = AsyncClient(
            headers=headers,
            timeout=self._timeout,
            transport=transport,
        )
        return self._client

    def _create_ephemeral_client(
        self,
        headers: dict[str, Any],
        retry: int | None = None,
        backoff: float | None = None,
    ) -> AsyncClient:
        """
        Create a single-use HTTP client with custom retry/backoff settings.

        The caller is responsible for closing the returned client.

        Args:
            headers (dict[str, Any]): The headers to use for the client.
            retry (int, optional): Override the number of retry attempts.
                Uses the pool default when not set.
            backoff (float, optional): Override the backoff factor.
                Uses the pool default when not set.

        Returns:
            AsyncClient: An ephemeral HTTP client.
        """
        if retry is not None:
            self._validate_retry_attempts(retry)
        if backoff is not None:
            self._validate_backoff_factor(backoff)

        retry_strategy = Retry(
            total=retry if retry is not None else self._retry.total,
            backoff_factor=(
                backoff if backoff is not None else self._retry.backoff_factor
            ),
            backoff_jitter=self._retry.backoff_jitter,
            allowed_methods=["POST"],
        )
        transport = RetryTransport(
            transport=AsyncHTTPTransport(),
            retry=retry_strategy,
        )
        return AsyncClient(
            headers=headers,
            timeout=self._timeout,
            transport=transport,
        )

    @property
    def is_shutdown(self) -> bool:
        """Whether the pool has been explicitly shut down."""
        return self._shutdown

    async def shutdown(self) -> None:
        """Close all clients and release their connections."""
        self._shutdown = True
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    @staticmethod
    def _validate_retry_attempts(retry_attempts: int) -> None:
        if not isinstance(retry_attempts, int) or retry_attempts < 0:
            raise ValueError("retry_attempts must be a positive integer")

    @staticmethod
    def _validate_backoff_factor(backoff_factor: float) -> None:
        if not isinstance(backoff_factor, (int, float)) or backoff_factor < 0:
            raise ValueError("backoff_factor must be a positive number")

    @staticmethod
    def _validate_backoff_jitter(backoff_jitter: float) -> None:
        if not isinstance(backoff_jitter, (int, float)) or backoff_jitter < 0:
            raise ValueError("backoff_jitter must be a positive number")

    @staticmethod
    def _validate_timeout(timeout: float) -> None:
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("timeout must be a positive number")

    @property
    def limits(self) -> Limits:
        """
        Get the current connection limits.

        Returns:
            Limits: The current connection limits configuration.
        """
        return self._limits

    def __repr__(self) -> str:
        return (
            f"ConnectionPool("
            f"max_connections={self._limits.max_connections}, "
            f"max_keepalive_connections={self._limits.max_keepalive_connections}, "  # noqa: E501
            f"keepalive_expiry={self._limits.keepalive_expiry}, "
            f"retry_attempts={self._retry.total}, "
            f"backoff_factor={self._retry.backoff_factor}, "
            f"backoff_jitter={self._retry.backoff_jitter}, "
            f"timeout={self._timeout})"
        )

    def __str__(self) -> str:
        return repr(self)
