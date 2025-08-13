from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import Self, override

from .._graphql_client import DimensionIdentifierFragment
from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .dimension_name import DimensionName
from .identifier import Identifier


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class DimensionIdentifier(Identifier):
    """The identifier of a :attr:`~atoti.Hierarchy.dimension` in the context of a :class:`~atoti.Cube`."""

    dimension_name: DimensionName
    _: KW_ONLY

    @classmethod
    def _from_graphql(cls, identifier: DimensionIdentifierFragment, /) -> Self:
        return cls(identifier.name)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.dimension_name!r})"
