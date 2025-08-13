from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._collections import FrozenSequence
from .._graphql_client import SelectionFieldIdentifier as SelectionFieldIdentifierInput
from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .column_name import ColumnName
from .identifier import Identifier
from .join_name import JoinName


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class SelectionFieldIdentifier(Identifier):
    """The identifier of a selection field in the context of a :class:`~atoti.Cube`."""

    join_names: FrozenSequence[JoinName]
    column_name: ColumnName
    _: KW_ONLY

    @property
    def _graphql_input(self) -> SelectionFieldIdentifierInput:
        return SelectionFieldIdentifierInput(
            join_names=list(self.join_names),
            column_name=self.column_name,
        )

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.join_names!r}, {self.column_name!r})"
