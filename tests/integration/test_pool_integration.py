import asyncio

import pytest
from httpx import Response

from async_sendgrid.exception import SessionClosedException
from async_sendgrid.pool import ConnectionPool


@pytest.fixture
def pool():
    return ConnectionPool(
        max_connections=2,
        max_keepalive_connections=0,
        keepalive_expiry=1.0,
    )


@pytest.mark.asyncio
async def test_concurrent_requests(pool: ConnectionPool):
    """Test making concurrent requests with the same client."""
    headers = {"Authorization": "Bearer test"}
    client = pool._create_client(headers)

    # Make concurrent requests
    tasks = []
    for _ in range(10):
        tasks.append(
            asyncio.create_task(client.get("http://localhost:3000/api/mails"))
        )

    responses = await asyncio.gather(*tasks)

    assert all(response.status_code == 200 for response in responses)
