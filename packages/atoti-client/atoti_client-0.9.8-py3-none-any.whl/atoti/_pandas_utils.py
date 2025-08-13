from __future__ import annotations

import sys
from collections.abc import Collection, Mapping
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
from pandas.core.indexes.datetimes import DatetimeIndex

from ._arrow_utils import get_arrow_type
from ._data_type import DataType

_COLUMN_LEVEL_SEPARATOR = "_"

_MIN_INT64 = -sys.maxsize - 1

_M8_NS = "<M8[ns]"


def pandas_to_arrow(  # pyright: ignore[reportUnknownParameterType]
    dataframe: pd.DataFrame,
    /,
    *,
    data_types: Mapping[str, DataType],
) -> pa.Table:
    dataframe = _clean_index(dataframe)
    dataframe = _stringify_column_names(dataframe)
    dataframe.columns = _flatten_multilevel_columns(dataframe.columns)
    date_without_time_column_names = _get_date_without_time_column_names(dataframe)
    schema = pa.Schema.from_pandas(dataframe)
    schema = _constrain_schema(
        schema,
        data_types=data_types,
        date_without_time_column_names=date_without_time_column_names,
    )
    return pa.Table.from_pandas(dataframe, schema=schema)


def _constrain_schema(  # pyright: ignore[reportUnknownParameterType]
    schema: pa.Schema,  # pyright: ignore[reportUnknownParameterType]
    /,
    *,
    data_types: Mapping[str, DataType],
    date_without_time_column_names: Collection[str],
) -> pa.Schema:
    """Force the types in the arrow schema with the requested type constraints.

    Additionally, due to differing behavior between Windows and Unix operating systems, if no type is specified for arrays, the largest type is forced.
    This is because the default integer type for Numpy arrays (the underlying data structure used for arrays in a Pandas Dataframe) is C ``long`` (https://docs.scipy.org/doc/numpy-1.10.1/user/basics.types.html).
    On most 64-bit operating systems, this is ``int64``, however on Windows it is represented by ``int32`` (https://docs.microsoft.com/en-us/cpp/c-language/storage-of-basic-types?view=msvc-160).
    Forcing the largest type when none is specified ensures consistent behavior of the Parquet serialization on all operating systems.
    This behavior does not override the type specified by the user if there is one.
    """
    for field_name in schema.names:
        field = schema.field(field_name)
        index = schema.get_field_index(field_name)
        new_field = None
        # If the type is set, we force the type in the schema
        if field_name in data_types:
            arrow_type = get_arrow_type(data_types[field_name])
            new_field = pa.field(
                field_name,
                arrow_type if arrow_type is not None else schema.field(index).type,
            )
        elif field_name in date_without_time_column_names:
            new_field = pa.field(
                field_name,
                get_arrow_type("LocalDate"),
            )
        elif field.type == pa.list_(pa.int32()):
            new_field = pa.field(field_name, pa.list_(pa.int64()))
        elif field.type == pa.list_(pa.float32()):
            new_field = pa.field(field_name, pa.list_(pa.float64()))
        if new_field is not None:
            schema = schema.set(index, new_field)
    return schema


def _flatten_multilevel_columns(columns: pd.Index[Any], /) -> pd.Index[Any]:
    return pd.Index(
        _COLUMN_LEVEL_SEPARATOR.join(
            map(str, (level for level in column if not pd.isnull(level))),
        )
        if isinstance(column, tuple)
        else column
        # `pandas` implements this method on `pd.Index` for "compatibility with subclass implementations".
        for column in columns.to_flat_index()  # type: ignore[no-untyped-call]
    )


def _stringify_column_names(dataframe: pd.DataFrame, /) -> pd.DataFrame:
    columns_to_rename = {
        column: str(column) for column in dataframe if not isinstance(column, str)
    }
    return (
        dataframe.rename(columns=columns_to_rename) if columns_to_rename else dataframe
    )


def _clean_index(data: pd.DataFrame, /) -> pd.DataFrame:
    """Un-index the dataframe.

    The named indices are moved to regular columns and the unnamed ones are dropped.
    """
    # Move named columns out of the index.
    dataframe = data.reset_index(
        level=[
            column_name
            for column_name in data.index.names
            # `index.names` can actually contain some `None` values.
            if column_name is not None  # pyright: ignore[reportUnnecessaryComparison]
        ],
        drop=False,
    )

    # Get rid of the remaining (unnamed) columns.
    return dataframe.reset_index(drop=True)


def _get_category_underlying_dtype(series: pd.Series[Any], /) -> object:
    return series.cat.categories.dtype


def _get_date_without_time_column_names(dataframe: pd.DataFrame, /) -> list[str]:
    return [
        column
        for column in dataframe.columns
        if (
            dataframe[column].dtype == np.dtype(_M8_NS)
            or (
                dataframe[column].dtype == "category"
                and _get_category_underlying_dtype(dataframe[column])
                == np.dtype(_M8_NS)
            )
        )
        and _contains_only_dates_without_time(dataframe[column])
    ]


def _contains_only_dates_without_time(values: pd.Series[Any], /) -> bool:
    # Copied from: https://github.com/pandas-dev/pandas/blob/fd67546153ac6a5685d1c7c4d8582ed1a4c9120f/pandas/io/formats/format.py#L1684
    date_values = DatetimeIndex(values)
    if date_values.tz is not None:  # pyright: ignore[reportAttributeAccessIssue]
        return False

    values_int = date_values.asi8  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
    consider_values = values_int != ...
    final_consider_values = [
        # None types are represented with the minimum 64bit integer in the date index
        int_value != _MIN_INT64 and consider_value
        for int_value, consider_value in zip(values_int, consider_values, strict=True)
    ]
    one_day_nanos = 86400 * 1e9
    even_days = (
        np.logical_and(
            final_consider_values,
            values_int % int(one_day_nanos) != 0,
        ).sum()
        == 0
    )
    return bool(even_days)
