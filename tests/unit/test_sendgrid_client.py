import pytest

from async_sendgrid.sendgrid import SendgridAPI

@pytest.fixture
def client() -> SendgridAPI:
    secret_key = "SECRET_KEY"
    impersonate_subuser = "John Smith"
    client = SendgridAPI(
        api_key=secret_key, impersonate_subuser=impersonate_subuser
    )
    return client

def test_constructor(client: SendgridAPI) -> None:
    """
    Test constructor.
    """
    assert client.endpoint == "https://api.sendgrid.com/v3/mail/send"
    assert client.api_key == "SECRET_KEY"
    assert client.headers == {
        "Authorization": "Bearer SECRET_KEY",
        "User-Agent": "sendgrid-async;python",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "On-Behalf-Of": "John Smith",
    }
