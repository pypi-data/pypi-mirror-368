from __future__ import annotations

from collections.abc import Mapping, Sequence, Set as AbstractSet

from ._client import Client
from ._graphql_client import (
    GetCubeReachableColumns,
    GetCubeReachableColumnsDatabaseDataModelDatabaseTables,
)
from ._identification import (
    ColumnIdentifier,
    CubeIdentifier,
    JoinIdentifier,
    TableIdentifier,
)
from ._selection_field import SelectionField


def _visit_table(
    table_identifier: TableIdentifier,
    /,
    *,
    column_identifiers: AbstractSet[ColumnIdentifier],
    join_identifiers: Sequence[JoinIdentifier],
    selection_field_from_column_identifier: dict[ColumnIdentifier, SelectionField],
    table_from_identifier: Mapping[
        TableIdentifier, GetCubeReachableColumnsDatabaseDataModelDatabaseTables
    ],
) -> None:
    table = table_from_identifier[table_identifier]

    for column in table.columns:
        column_identifier = ColumnIdentifier(
            table_identifier=table_identifier,
            column_name=column.name,
        )

        if column_identifier not in column_identifiers:
            continue

        if (
            existing_selection_field_identifier
            := selection_field_from_column_identifier.get(column_identifier)
        ) is not None:
            raise RuntimeError(
                f"{column_identifier} is reachable from different paths: {existing_selection_field_identifier.join_identifiers} and {join_identifiers}. "
            )

        selection_field_from_column_identifier[column_identifier] = SelectionField(
            join_identifiers, column_identifier
        )

    for join in table.joins:
        _visit_table(
            TableIdentifier._from_graphql(join.target),
            column_identifiers=column_identifiers,
            join_identifiers=[*join_identifiers, JoinIdentifier._from_graphql(join)],
            selection_field_from_column_identifier=selection_field_from_column_identifier,
            table_from_identifier=table_from_identifier,
        )


def _get_selection_field_from_column_identifier(
    cube_reachable_columns: GetCubeReachableColumns,
    /,
    *,
    column_identifiers: AbstractSet[ColumnIdentifier],
) -> dict[ColumnIdentifier, SelectionField]:
    fact_table_identifier = TableIdentifier._from_graphql(
        cube_reachable_columns.cube_data_model.cube.fact_table
    )
    selection_field_from_column_identifier: dict[ColumnIdentifier, SelectionField] = {}
    table_from_identifier = {
        TableIdentifier._from_graphql(table): table
        for table in cube_reachable_columns.database_data_model.database.tables
    }
    _visit_table(
        fact_table_identifier,
        column_identifiers=column_identifiers,
        join_identifiers=[],
        selection_field_from_column_identifier=selection_field_from_column_identifier,
        table_from_identifier=table_from_identifier,
    )
    return selection_field_from_column_identifier


def get_selection_field_from_column_identifier(
    column_identifiers: AbstractSet[ColumnIdentifier],
    /,
    *,
    client: Client,
    cube_identifier: CubeIdentifier,
) -> dict[ColumnIdentifier, SelectionField]:
    if not column_identifiers:
        return {}

    output = client._require_graphql_client().get_cube_reachable_columns(
        cube_name=cube_identifier.cube_name
    )
    return _get_selection_field_from_column_identifier(
        output, column_identifiers=column_identifiers
    )
