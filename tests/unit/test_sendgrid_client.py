import pytest

from async_sendgrid.sendgrid import SendgridAPI


@pytest.fixture
def client() -> SendgridAPI:
    secret_key = "SECRET_KEY"
    on_behalf_of = "John Smith"
    client = SendgridAPI(api_key=secret_key, on_behalf_of=on_behalf_of)
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


def test_repr(client: SendgridAPI) -> None:
    """
    Test __repr__ method.
    """
    assert repr(client) == (
        "SendgridAPI("
        "endpoint='https://api.sendgrid.com/v3/mail/send', "
        "pool=ConnectionPool("
        "max_connections=10, "
        "max_keepalive_connections=5, "
        "keepalive_expiry=5.0, "
        "retry_attempts=5, "
        "backoff_factor=0.5, "
        "backoff_jitter=1.0))"
    )
    assert str(client) == repr(client)
