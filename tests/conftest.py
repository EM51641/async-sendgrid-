import asyncio

import pytest

# Configure pytest-asyncio to use the 'auto' mode
pytest_plugins = ("pytest_asyncio",)


# Set the event loop policy to 'auto'
def pytest_configure(config):
    config.option.asyncio_mode = "auto"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
