from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import Self, override

from .._graphql_client import MeasureIdentifierFragment
from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .identifier import Identifier
from .measure_name import MeasureName


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class MeasureIdentifier(Identifier):
    """The identifier of a :class:`~atoti.Measure` in the context of a :class:`~atoti.Cube`."""

    measure_name: MeasureName
    _: KW_ONLY

    @classmethod
    def _from_graphql(cls, identifier: MeasureIdentifierFragment, /) -> Self:
        return cls(identifier.name)

    @override
    def __repr__(self) -> str:
        return f"m[{self.measure_name!r}]"
