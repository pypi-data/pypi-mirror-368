from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import Self, override

from .._graphql_client import TableIdentifierFragment
from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .identifier import Identifier
from .table_name import TableName


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class TableIdentifier(Identifier):
    """The identifier of a :class:`~atoti.Table` in the context of a :class:`~atoti.Session`."""

    table_name: TableName
    _: KW_ONLY

    @classmethod
    def _from_graphql(cls, identifier: TableIdentifierFragment, /) -> Self:
        return cls(identifier.name)

    @override
    def __repr__(self) -> str:
        return f"t[{self.table_name!r}]"
