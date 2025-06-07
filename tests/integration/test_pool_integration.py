import asyncio

import pytest
from httpx import Response

from async_sendgrid.exception import SessionClosedException
from async_sendgrid.pool import ConnectionPool


@pytest.fixture
def pool():
    return ConnectionPool(
        max_connections=2,
        max_keepalive_connections=1,
        keepalive_expiry=1.0,
    )


@pytest.mark.asyncio
async def test_concurrent_requests(pool: ConnectionPool):
    """Test making concurrent requests with the same client."""
    headers = {"Authorization": "Bearer test"}
    client = pool._create_client(headers)

    # Make two concurrent requests
    response1 = await client.get("http://localhost:3000/api/mails")
    response2 = await client.get("http://localhost:3000/api/mails")

    assert response1.status_code == 200
    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_client_reuse(pool: ConnectionPool):
    """Test that the same client can be reused for multiple requests."""
    headers = {"Authorization": "Bearer test"}
    client = pool._create_client(headers)

    # First request
    response1 = await client.get("http://localhost:3000/api/mails")
    assert response1.status_code == 200

    # Second request with the same client
    response2 = await client.get("http://localhost:3000/api/mails")
    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_multiple_clients(pool: ConnectionPool):
    """Test using multiple clients from the same pool."""
    headers = {"Authorization": "Bearer test"}

    # Create two clients
    client1 = pool._create_client(headers)
    client2 = pool._create_client(headers)

    # Make requests with both clients
    response1 = await client1.get("http://localhost:3000/api/mails")
    response2 = await client2.get("http://localhost:3000/api/mails")

    assert response1.status_code == 200
    assert response2.status_code == 200
