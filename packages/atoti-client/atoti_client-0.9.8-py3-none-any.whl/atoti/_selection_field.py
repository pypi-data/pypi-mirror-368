from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from ._collections import FrozenSequence
from ._graphql_client import SelectionFieldIdentifierFragment
from ._identification import ColumnIdentifier, JoinIdentifier, SelectionFieldIdentifier
from ._pydantic import PYDANTIC_CONFIG


@final
@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class SelectionField:
    join_identifiers: FrozenSequence[JoinIdentifier]
    column_identifier: ColumnIdentifier
    _: KW_ONLY

    @classmethod
    def _from_graphql(cls, identifier: SelectionFieldIdentifierFragment, /) -> Self:
        return cls(
            tuple(JoinIdentifier._from_graphql(join) for join in identifier.joins),
            ColumnIdentifier._from_graphql(identifier.column),
        )

    @property
    def _identifier(self) -> SelectionFieldIdentifier:
        return SelectionFieldIdentifier(
            join_names=tuple(
                identifier.join_name for identifier in self.join_identifiers
            ),
            column_name=self.column_identifier.column_name,
        )
