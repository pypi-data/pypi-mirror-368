from collections.abc import Mapping, Sequence, Set as AbstractSet
from dataclasses import KW_ONLY
from typing import Annotated, final

from pydantic import Field
from pydantic.dataclasses import dataclass

from ._collections import frozendict
from ._constant import Constant
from ._data_type import DataType
from ._identification import ColumnName
from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class TableDefinition:
    """The definition to create a :class:`~atoti.Table`."""

    data_types: Annotated[Mapping[ColumnName, DataType], Field(min_length=1)]
    """The table column names and their corresponding :mod:`data type <atoti.type>`."""

    _: KW_ONLY

    default_values: Mapping[ColumnName, Constant | None] = frozendict()
    """Mapping from column name to column :attr:`~atoti.Column.default_value`."""

    keys: AbstractSet[ColumnName] | Sequence[ColumnName] = frozenset()
    """The columns that will become :attr:`~atoti.Table.keys` of the table.

    If a :class:`~collections.abc.Set` is given, the table keys will be ordered as the keys of :attr:`data_type`.
    """

    partitioning: str | None = None
    """The definition of how the data will be split across partitions."""

    def __post_init__(self) -> None:
        column_names = frozenset(self.data_types)

        invalid_default_value_keys = set(self.default_values) - column_names
        if invalid_default_value_keys:
            raise ValueError(
                f"Default values are provided for columns `{invalid_default_value_keys}` which are not part of the passed columns: `{sorted(column_names)}`."
            )

        invalid_keys = set(self.keys) - column_names
        if invalid_keys:
            raise ValueError(
                f"Keys `{invalid_keys}` are not part of the passed columns: `{sorted(column_names)}`."
            )
