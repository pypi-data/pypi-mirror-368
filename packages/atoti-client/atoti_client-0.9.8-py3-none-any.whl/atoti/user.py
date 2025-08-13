from collections.abc import Set as AbstractSet
from typing import final

from pydantic.dataclasses import dataclass

from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class User:
    name: str
    roles: AbstractSet[str]
