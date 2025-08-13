import re
from collections.abc import Collection

import pandas as pd
import pyarrow as pa

from .._identification import LevelIdentifier

_LEVEL_UNIQUE_NAME_PATTERN = re.compile(
    r"^\[(?P<dimension>.*)\]\.\[(?P<hierarchy>.*)\]\.\[(?P<level>.*)\]$",
)


def _parse_level_identifier(
    level_unique_name: str,
) -> LevelIdentifier | None:
    match = _LEVEL_UNIQUE_NAME_PATTERN.match(level_unique_name)

    return (
        LevelIdentifier.from_key(
            (match.group("dimension"), match.group("hierarchy"), match.group("level"))
        )
        if match
        else None
    )


# See https://arrow.apache.org/docs/python/pandas.html#nullable-types.
# Only types that can be sent by Atoti Server are listed.
_PANDAS_NULLABLE_DTYPE_FROM_ARROW_DATA_TYPE = {
    pa.int32(): pd.Int32Dtype(),
    pa.int64(): pd.Int64Dtype(),
    pa.bool_(): pd.BooleanDtype(),
    pa.float32(): pd.Float32Dtype(),
    pa.float64(): pd.Float64Dtype(),
    pa.string(): pd.StringDtype(),
}


def pandas_from_arrow(
    table: pa.Table,  # pyright: ignore[reportUnknownParameterType]
) -> pd.DataFrame:
    # Fast for small tables (less than 100k lines) but can take several seconds for larger ones.
    dataframe: pd.DataFrame = table.to_pandas(
        # The level columns could stay non nullable but there is no fast way to handle them differently than measure columns.
        types_mapper=_PANDAS_NULLABLE_DTYPE_FROM_ARROW_DATA_TYPE.get,
    )
    column_names: Collection[str] = table.column_names
    level_identifier = {
        column_name: _parse_level_identifier(column_name)
        for column_name in column_names
    }
    return dataframe.rename(
        columns={
            column_name: level_identifier.level_name
            for column_name, level_identifier in level_identifier.items()
            if level_identifier is not None
        },
    )
