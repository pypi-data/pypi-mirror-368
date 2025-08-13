from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .identifier import Identifier
from .query_cube_name import QueryCubeName


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class QueryCubeIdentifier(Identifier):
    """The identifier of a :class:`~atoti.QueryCube` in the context of a :class:`~atoti.QuerySession`."""

    cube_name: QueryCubeName
    _: KW_ONLY

    @override
    def __repr__(self) -> str:
        return f"query_cubes[{self.cube_name!r}]"
