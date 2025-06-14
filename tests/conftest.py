from typing import Generator

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


@pytest.fixture(scope="package")
def provider() -> Generator[TracerProvider, None, None]:
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    yield provider
    provider.shutdown()
