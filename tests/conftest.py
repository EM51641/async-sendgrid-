from typing import Generator

import pytest
from httpx import request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


@pytest.fixture(scope="package")
def provider() -> Generator[TracerProvider, None, None]:
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    yield provider
    provider.shutdown()


@pytest.fixture(autouse=True)
def cleanup_test_server():
    yield
    request("DELETE", url="http://localhost:3000/api/mails")
