from importlib.metadata import version

from .sendgrid import SendgridAPI  # noqa

__version__ = version("sendgrid-async")
__all__ = ["SendgridAPI"]
