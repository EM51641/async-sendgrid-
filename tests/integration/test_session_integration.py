from async_sendgrid.utils import create_session


def test_header_while_creating_session():
    """
    Test create_session utils.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Zm9vOmJhcg==",
        "grant_type": "client_credentials",
    }
    session = create_session(headers)
    assert session.headers["Content-Type"] == "application/json"
    assert session.headers["Authorization"] == "Zm9vOmJhcg=="
    assert session.headers["grant_type"] == "client_credentials"
