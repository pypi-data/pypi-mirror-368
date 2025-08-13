from typing import TypeAlias, final

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .._collections import FrozenMapping, FrozenSequence
from .._pydantic import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    create_camel_case_alias_generator,
)

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ServerApiVersion:
    id: str
    rest_path: str | None = None
    ws_path: str | None = None


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ServerApi:
    versions: FrozenSequence[ServerApiVersion]


_Namespace: TypeAlias = str


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ServerVersions:
    version: int
    server_version: str
    apis: FrozenMapping[_Namespace, ServerApi]
