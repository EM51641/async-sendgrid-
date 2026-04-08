from importlib.metadata import version

from .sendgrid import SendgridAPI  # noqa

try:
    from importlib.metadata import version

    __version__ = version("sendgrid-async")
except Exception:
    __version__ = "0.0.0-dev"

__all__ = ["SendgridAPI"]
