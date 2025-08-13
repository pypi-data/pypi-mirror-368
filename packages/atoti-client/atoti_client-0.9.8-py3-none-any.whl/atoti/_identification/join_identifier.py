from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import Self, override

from .._graphql_client import JoinIdentifierFragment
from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .identifier import Identifier
from .join_name import JoinName
from .table_identifier import TableIdentifier


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class JoinIdentifier(Identifier):
    """The identifier of a join in the context of a :class:`~atoti.Session`."""

    source_table_identifier: TableIdentifier
    join_name: JoinName
    _: KW_ONLY

    @classmethod
    def _from_graphql(cls, identifier: JoinIdentifierFragment, /) -> Self:
        return cls(
            TableIdentifier._from_graphql(identifier.source),
            identifier.name,
        )

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.source_table_identifier!r}, {self.join_name!r})"
