from importlib.metadata import version

from .sendgrid import SendgridAPI  # noqa
from .pool import ConnectionPool  # noqa

__version__ = "0.0.0-dev"

try:

    __version__ = version("sendgrid-async")
except Exception:
    pass

__all__ = ["SendgridAPI", "ConnectionPool"]
