"""This module is deprecated, import ``HttpRequest`` from :class:`atoti.endpoint.Request` and ``User`` from :class:`atoti.User` instead."""

from .endpoint import (
    Request as HttpRequest,  # noqa: F401 # pyright: ignore[reportUnusedImport]
)
from .user import User  # noqa: F401 # pyright: ignore[reportUnusedImport]
