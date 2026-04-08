import time

import pytest
from pytest_httpserver import HTTPServer
from sendgrid import Mail  # type: ignore
from werkzeug.wrappers import Request, Response

from async_sendgrid.pool import ConnectionPool
from async_sendgrid.sendgrid import SendgridAPI


def _counting_handler(
    fail_count: int,
    fail_status: int = 503,
):
    """Return a handler that fails `fail_count` times then succeeds."""
    state = {"n": 0, "timestamps": []}

    def handler(request: Request) -> Response:
        state["timestamps"].append(time.monotonic())
        state["n"] += 1
        if state["n"] <= fail_count:
            return Response(
                status=fail_status,
                response=b"error",
            )
        return Response(status=202, response=b"ok")

    return handler, state


@pytest.fixture
def email() -> Mail:
    return Mail(
        from_email="johndoe@example.com",
        to_emails="janedoe@example.com",
        subject="Test",
        plain_text_content="Hello",
    )


@pytest.fixture
def pool() -> ConnectionPool:
    return ConnectionPool(backoff_factor=1, backoff_jitter=0.0)


def _make_client(
    httpserver: HTTPServer,
    pool: ConnectionPool,
) -> SendgridAPI:
    return SendgridAPI(
        api_key="test-key",
        endpoint=httpserver.url_for("/v3/mail/send"),
        pool=pool,
    )


@pytest.mark.asyncio
async def test_default_retry(
    httpserver: HTTPServer,
    email: Mail,
    pool: ConnectionPool,
):
    """Pool default retry recovers from transient failures."""
    handler, state = _counting_handler(fail_count=2)
    httpserver.expect_request(
        "/v3/mail/send", method="POST"
    ).respond_with_handler(handler)

    client = _make_client(httpserver, pool)
    response = await client.send(email)

    assert response.status_code == 202
    assert state["n"] == 3


@pytest.mark.asyncio
async def test_default_backoff(
    httpserver: HTTPServer,
    email: Mail,
    pool: ConnectionPool,
):
    """Pool default backoff (0.5) produces expected delay."""
    handler, state = _counting_handler(fail_count=1)
    httpserver.expect_request(
        "/v3/mail/send", method="POST"
    ).respond_with_handler(handler)

    client = _make_client(httpserver, pool)
    response = await client.send(email)

    assert response.status_code == 202

    # expected backoff is 0.5 * 2 = 1.0s

    gap = state["timestamps"][1] - state["timestamps"][0]
    assert 1.75 <= gap <= 2.25, f"Expected ~2.0s backoff, got {gap:.2f}s"


@pytest.mark.asyncio
async def test_override_retry(
    httpserver: HTTPServer,
    email: Mail,
    pool: ConnectionPool,
):
    """Per-call retry override changes the number of attempts."""
    handler, state = _counting_handler(fail_count=2)
    httpserver.expect_request(
        "/v3/mail/send", method="POST"
    ).respond_with_handler(handler)

    client = _make_client(httpserver, pool)
    response = await client.send(email, retry=2)

    assert response.status_code == 202
    assert state["n"] == 3


@pytest.mark.asyncio
async def test_override_backoff(
    httpserver: HTTPServer,
    email: Mail,
    pool: ConnectionPool,
):
    """Per-call backoff override changes the delay between retries."""
    handler, state = _counting_handler(fail_count=1)
    httpserver.expect_request(
        "/v3/mail/send", method="POST"
    ).respond_with_handler(handler)

    client = _make_client(httpserver, pool)
    response = await client.send(email, retry=1, backoff=2.0)

    assert response.status_code == 202

    # expected backoff is 2.0 * 2 = 4.0s
    gap = state["timestamps"][1] - state["timestamps"][0]
    assert 3.75 <= gap <= 4.25, f"Expected ~4.0s backoff, got {gap:.2f}s"
