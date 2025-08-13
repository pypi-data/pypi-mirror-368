from __future__ import annotations

from collections.abc import Collection, Mapping

import pandas as pd

from .._column_definition import ColumnDefinition
from .._data_type import DataType
from .convert_series import convert_series


def create_dataframe(
    rows: Collection[tuple[object, ...]],
    columns_or_types: Collection[ColumnDefinition] | Mapping[str, DataType],
    /,
) -> pd.DataFrame:
    """Return a DataFrame with columns of the given types."""
    columns: Collection[ColumnDefinition] = (
        [
            ColumnDefinition(
                # Pyright fails to see that the `isinstance` below ensures that `name` is a string.
                name=name,  # pyright: ignore[reportArgumentType]
                data_type=data_type,
            )
            for name, data_type in columns_or_types.items()
        ]
        if isinstance(columns_or_types, Mapping)
        else columns_or_types
    )

    dataframe = pd.DataFrame(
        rows,
        columns=[columns.name for columns in columns],
        dtype="object",  # To prevent any preliminary conversion.
    )

    for column in columns:
        converted_series = convert_series(
            dataframe[column.name],
            data_type=column.data_type,
            nullable=column.nullable,
        )
        dataframe[column.name] = converted_series

    return dataframe
