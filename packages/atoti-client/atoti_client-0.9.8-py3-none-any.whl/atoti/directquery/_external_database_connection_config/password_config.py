from abc import ABC

from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class PasswordConfig(ABC):  # noqa: B024
    password: str | None = None
    """The password to connect to the database.

    Passing it in this separate attribute prevents it from being logged alongside the connection string.

    If ``None``, a password is expected to be present in :attr:`url`.
    """
