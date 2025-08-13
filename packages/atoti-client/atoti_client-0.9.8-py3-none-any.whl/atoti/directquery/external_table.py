from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from typing import Final, Generic, final

from typing_extensions import deprecated, override

from .._collections import frozendict
from .._data_type import DataType
from .._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from .._identification import (
    ColumnName,
    ExternalColumnIdentifier,
    ExternalTableIdentifier,
    HasIdentifier,
    TableName,
)
from .._ipython import ReprJson, ReprJsonable
from ._external_database_connection_config import ExternalDatabaseConnectionConfigT
from .external_column import ExternalColumn


@final
# Not inheriting from `Mapping` for the same reasons as `Table`.
class ExternalTable(
    Generic[ExternalDatabaseConnectionConfigT],
    HasIdentifier[ExternalTableIdentifier],
    ReprJsonable,
):
    """Table of an external database."""

    def __init__(
        self,
        identifier: ExternalTableIdentifier,
        /,
        *,
        database_key: str,
        get_data_types: Callable[[], dict[str, DataType]],
    ) -> None:
        self._database_key: Final = database_key
        self._get_data_types: Final = get_data_types
        self.__identifier: Final = identifier

    @property
    def _data_types(self) -> frozendict[ColumnName, DataType]:
        return frozendict(self._get_data_types())

    @override
    def _repr_json_(self) -> ReprJson:
        return dict(self._data_types), {
            "expanded": True,
            "root": self._identifier.table_name,
        }

    @property
    def name(self) -> TableName:
        """Name of the table."""
        return self._identifier.table_name

    @property
    @deprecated(
        "`ExternalTable.columns` is deprecated, use `list(table)` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def columns(self) -> Sequence[ColumnName]:
        """Names of the columns of the table.

        :meta private:
        """
        return list(self)

    @property
    @override
    def _identifier(self) -> ExternalTableIdentifier:
        return self.__identifier

    def __getitem__(self, column_name: ColumnName, /) -> ExternalColumn:
        # Same signature as `Mapping.__getitem__()`.
        if column_name not in self._data_types:
            raise KeyError(column_name)

        return ExternalColumn(
            ExternalColumnIdentifier(self._identifier, column_name),
            get_data_type=lambda: self._data_types[column_name],
        )

    def __iter__(self) -> Iterator[ColumnName]:
        # Same signature as `Mapping.__iter__()`.
        return iter(self._data_types)
