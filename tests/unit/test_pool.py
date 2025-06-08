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


def test_pool_initialization():
    """Test pool initialization with default values."""
    pool = ConnectionPool()
    assert pool.limits.max_connections == 10
    assert pool.limits.max_keepalive_connections == 5
    assert pool.limits.keepalive_expiry == 5.0


def test_pool_initialization_custom():
    """Test pool initialization with custom values."""
    pool = ConnectionPool(
        max_connections=5,
        max_keepalive_connections=2,
        keepalive_expiry=3.0,
    )
    assert pool.limits.max_connections == 5
    assert pool.limits.max_keepalive_connections == 2
    assert pool.limits.keepalive_expiry == 3.0


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


def test_pool_string_representation(pool: ConnectionPool):
    """Test string representation of the pool."""
    pool_str = str(pool)
    assert "ConnectionPool" in pool_str
    assert "max_connections=2" in pool_str
    assert "max_keepalive=1" in pool_str
    assert "keepalive_expiry=1.0" in pool_str
