from __future__ import annotations

from abc import ABC
from dataclasses import field
from typing import Literal, final

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .._collections import FrozenMapping, FrozenSequence
from .._pydantic import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    create_camel_case_alias_generator,
)

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(
        force_aliased_attribute_names={"is_directory"},
    ),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class _ContentEntry(ABC):
    timestamp: int
    last_editor: str
    owners: FrozenSequence[str]
    readers: FrozenSequence[str]
    can_read: bool
    can_write: bool


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class DirectoryContentEntry(_ContentEntry):
    is_directory: Literal[True] = field(default=True, repr=False)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class DirectoryContentTree:
    entry: DirectoryContentEntry
    children: FrozenMapping[str, ContentTree] = field(default_factory=dict)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class FileContentEntry(_ContentEntry):
    content: str
    is_directory: Literal[False] = field(default=False, repr=False)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class FileContentTree:
    entry: FileContentEntry


ContentTree = DirectoryContentTree | FileContentTree
