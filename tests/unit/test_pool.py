import pytest
from httpx import AsyncClient

from async_sendgrid.pool import ConnectionPool


@pytest.fixture
def pool():
    return ConnectionPool(
        max_connections=2,
        max_keepalive_connections=1,
        keepalive_expiry=1.0,
    )


def test_pool_default_initialization():
    """Test pool initialization with default values."""
    pool = ConnectionPool()
    assert pool.limits.max_connections == 10
    assert pool.limits.max_keepalive_connections == 5
    assert pool.limits.keepalive_expiry == 5.0
    assert pool._retry.total == 5
    assert pool._retry.backoff_factor == 0.5
    assert pool._retry.backoff_jitter == 1.0


def test_pool_custom_initialization():
    """Test pool initialization with custom values."""
    pool = ConnectionPool(
        max_connections=5,
        max_keepalive_connections=2,
        keepalive_expiry=3.0,
        retry_attempts=3,
        backoff_factor=1.0,
        backoff_jitter=0.25,
    )
    assert pool.limits.max_connections == 5
    assert pool.limits.max_keepalive_connections == 2
    assert pool.limits.keepalive_expiry == 3.0
    assert pool._retry.total == 3
    assert pool._retry.backoff_factor == 1.0
    assert pool._retry.backoff_jitter == 0.25


def test_create_client(pool: ConnectionPool):
    """Test client creation with headers."""
    headers = {
        "Authorization": "Bearer test",
        "Cookie": "test_cookie=value",
        "Content-Type": "application/json",
    }
    client = pool._create_client(headers)

    assert isinstance(client, AsyncClient)
    # Check that our custom headers are present
    assert client.headers["Authorization"] == "Bearer test"
    assert client.headers["Cookie"] == "test_cookie=value"
    assert client.headers["Content-Type"] == "application/json"

    # Check that default headers are also present
    assert "accept" in client.headers
    assert "user-agent" in client.headers


def test_pool_repr(pool: ConnectionPool):
    """Test repr of the pool."""
    assert repr(pool) == (
        "ConnectionPool("
        "max_connections=2, "
        "max_keepalive_connections=1, "
        "keepalive_expiry=1.0, "
        "retry_attempts=5, "
        "backoff_factor=0.5, "
        "backoff_jitter=1.0)"
    )
    assert str(pool) == repr(pool)


@pytest.mark.parametrize("retry_attempts", [-1, -100, 1.5, "3", None])
def test_pool_invalid_retry_attempts_raises(retry_attempts):
    """Test that invalid retry_attempts raises ValueError."""
    with pytest.raises(ValueError, match="retry_attempts"):
        ConnectionPool(retry_attempts=retry_attempts)


@pytest.mark.parametrize("backoff_factor", [-0.5, -1, "0.5", None])
def test_pool_invalid_backoff_raises(backoff_factor):
    """Test that invalid backoff_factor raises ValueError."""
    with pytest.raises(ValueError, match="backoff_factor"):
        ConnectionPool(backoff_factor=backoff_factor)


@pytest.mark.parametrize("backoff_jitter", [-0.5, -1, "0.5", None])
def test_pool_invalid_jitter_raises(backoff_jitter):
    """Test that invalid backoff_jitter raises ValueError."""
    with pytest.raises(ValueError, match="backoff_jitter"):
        ConnectionPool(backoff_jitter=backoff_jitter)
