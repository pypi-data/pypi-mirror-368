from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import Self, override

from .._graphql_client import (
    LevelIdentifier as LevelIdentifierInput,
    LevelIdentifierFragment,
)
from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .hierarchy_identifier import HierarchyIdentifier
from .identifier import Identifier
from .level_key import (
    LevelUnambiguousKey,
    java_description_from_level_key,
    level_key_from_java_description,
    normalize_level_key,
)
from .level_name import LevelName


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class LevelIdentifier(Identifier):
    """The identifier of a :class:`~atoti.Level` in the context of a :class:`~atoti.Cube`."""

    hierarchy_identifier: HierarchyIdentifier
    level_name: LevelName
    _: KW_ONLY

    @classmethod
    def _from_graphql(cls, identifier: LevelIdentifierFragment, /) -> Self:
        return cls(
            HierarchyIdentifier._from_graphql(identifier.hierarchy),
            identifier.name,
        )

    @classmethod
    def _from_java_description(cls, java_description: str, /) -> Self:
        dimension_name, hierarchy_name, level_name = normalize_level_key(
            level_key_from_java_description(java_description)
        )
        assert dimension_name is not None
        assert hierarchy_name is not None
        return cls.from_key((dimension_name, hierarchy_name, level_name))

    @classmethod
    def from_key(cls, key: LevelUnambiguousKey, /) -> Self:
        dimension_name, hierarchy_name, level_name = key
        return cls(
            HierarchyIdentifier.from_key((dimension_name, hierarchy_name)),
            level_name,
        )

    @property
    def _graphql_input(self) -> LevelIdentifierInput:
        return LevelIdentifierInput(
            dimension_name=self.hierarchy_identifier.dimension_identifier.dimension_name,
            hierarchy_name=self.hierarchy_identifier.hierarchy_name,
            level_name=self.level_name,
        )

    @property
    def _java_description(self) -> str:
        return java_description_from_level_key(self.key)

    @property
    def key(self) -> LevelUnambiguousKey:
        return *self.hierarchy_identifier.key, self.level_name

    @override
    def __repr__(self) -> str:
        return f"l[{', '.join(repr(part) for part in self.key)}]"
