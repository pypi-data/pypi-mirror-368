from typing import Final, final

from typing_extensions import override

from ._client import Client
from ._collections import (
    DelegatingKeyDisambiguatingMapping,
    SupportsUncheckedMappingLookup,
)
from ._identification import ColumnIdentifier, ColumnName, TableIdentifier
from .column import Column


@final
class Columns(
    SupportsUncheckedMappingLookup[ColumnName, ColumnName, Column],
    DelegatingKeyDisambiguatingMapping[ColumnName, ColumnName, Column],
):
    def __init__(self, *, client: Client, table_identifier: TableIdentifier) -> None:
        self._client: Final = client
        self._table_identifier: Final = table_identifier

    @override
    def _create_lens(self, key: ColumnName, /) -> Column:
        return Column(
            ColumnIdentifier(self._table_identifier, key), client=self._client
        )

    @override
    def _get_unambiguous_keys(self, *, key: ColumnName | None) -> list[ColumnName]:
        if key is None:
            output = self._client._require_graphql_client().get_table_columns(
                table_name=self._table_identifier.table_name
            )
            return [column.name for column in output.data_model.database.table.columns]

        output = self._client._require_graphql_client().find_column(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
            column_name=key,
            table_name=self._table_identifier.table_name,
        )
        column = output.data_model.database.table.column  # type: ignore[attr-defined]
        return [] if column is None else [column.name]
