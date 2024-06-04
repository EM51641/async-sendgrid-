import toml  # type: ignore

from .sendgrid import SendgridAPI  # noqa

pyproject = toml.load("pyproject.toml")  # Extract the version
version = pyproject["tool"]["poetry"]["version"]

__version__ = version
__all__ = ["SendgridAPI"]
