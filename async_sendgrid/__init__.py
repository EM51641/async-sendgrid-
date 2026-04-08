from importlib.metadata import PackageNotFoundError, version

from .sendgrid import SendgridAPI  # noqa
from .pool import ConnectionPool  # noqa

__version__ = "0.0.0-dev"

try:
    __version__ = version("sendgrid-async")
except PackageNotFoundError:
    pass

__all__ = ["SendgridAPI", "ConnectionPool"]
