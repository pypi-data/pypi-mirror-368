from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import Self, override

from .._graphql_client import (
    HierarchyIdentifier as HierarchyIdentifierInput,
    HierarchyIdentifierFragment,
)
from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .dimension_identifier import DimensionIdentifier
from .hierarchy_key import HierarchyUnambiguousKey
from .hierarchy_name import HierarchyName
from .identifier import Identifier


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class HierarchyIdentifier(Identifier):
    """The identifier of a :class:`~atoti.Hierarchy` in the context of a :class:`~atoti.Cube`."""

    dimension_identifier: DimensionIdentifier
    hierarchy_name: HierarchyName
    _: KW_ONLY

    @classmethod
    def _from_graphql(cls, identifier: HierarchyIdentifierFragment, /) -> Self:
        return cls(
            DimensionIdentifier._from_graphql(identifier.dimension),
            identifier.name,
        )

    @classmethod
    def _from_java_description(cls, java_description: str, /) -> Self:
        hierarchy_name, dimension_name = java_description.split("@")
        return cls.from_key((dimension_name, hierarchy_name))

    @classmethod
    def from_key(cls, key: HierarchyUnambiguousKey, /) -> Self:
        dimension_name, hierarchy_name = key
        return cls(DimensionIdentifier(dimension_name), hierarchy_name)

    @property
    def _graphql_input(self) -> HierarchyIdentifierInput:
        return HierarchyIdentifierInput(
            dimension_name=self.dimension_identifier.dimension_name,
            hierarchy_name=self.hierarchy_name,
        )

    @property
    def _java_description(self) -> str:
        return "@".join(reversed(self.key))

    @property
    def key(self) -> HierarchyUnambiguousKey:
        return self.dimension_identifier.dimension_name, self.hierarchy_name

    @override
    def __repr__(self) -> str:
        return f"h[{', '.join(repr(part) for part in self.key)}]"
