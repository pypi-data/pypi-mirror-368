from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import Self, override

from .._graphql_client import CubeIdentifierFragment
from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .cube_name import CubeName
from .identifier import Identifier


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class CubeIdentifier(Identifier):
    """The identifier of a :class:`~atoti.Cube` in the context of a :class:`~atoti.Session`."""

    cube_name: CubeName
    _: KW_ONLY

    @classmethod
    def _from_graphql(cls, identifier: CubeIdentifierFragment, /) -> Self:
        return cls(identifier.name)

    @override
    def __repr__(self) -> str:
        return f"cubes[{self.cube_name!r}]"
