from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .._data_type import (
    DataType,
    get_numeric_array_element_type,
    is_array_type,
    is_date_type,
    is_numeric_array_type,
    is_numeric_type,
    is_time_type,
)
from .pandas_non_nullable_dtype_from_nullable_dtype import (
    pandas_non_nullable_dtype_from_nullable_dtype,
)
from .pandas_nullable_dtype_from_data_type import pandas_nullable_dtype_from_data_type

_ARRAY_SEPARATOR = ";"

_TIMEZONE_FIRST_CHARACTER = "["


def convert_series(
    series: pd.Series[Any],
    /,
    *,
    data_type: DataType,
    nullable: bool,
) -> pd.Series[Any]:
    if is_numeric_type(data_type) or data_type == "boolean" or data_type == "String":
        nullable_dtype = pandas_nullable_dtype_from_data_type(data_type)
        dtype = (
            nullable_dtype
            if nullable
            else pandas_non_nullable_dtype_from_nullable_dtype(nullable_dtype)
        )
        return series.astype(
            dtype,
        )

    if is_array_type(data_type):
        array_dtype = (
            pandas_non_nullable_dtype_from_nullable_dtype(
                pandas_nullable_dtype_from_data_type(
                    get_numeric_array_element_type(data_type),
                ),
            )
            if is_numeric_array_type(data_type)
            else "object"
        )
        return pd.Series(
            [
                None
                if array is None
                else np.array(
                    array.split(_ARRAY_SEPARATOR) if isinstance(array, str) else array,
                    dtype=array_dtype,
                )
                for array in series
            ],
            dtype="object",
            index=series.index,
        )

    if is_date_type(data_type):
        if data_type == "ZonedDateTime":
            date_times = [
                pd.to_datetime(
                    # Keep offset but remove time zone name that pandas cannot parse.
                    zoned_date_time.split(_TIMEZONE_FIRST_CHARACTER, maxsplit=1)[0]
                    if isinstance(zoned_date_time, str)
                    else zoned_date_time,
                )
                for zoned_date_time in series
            ]
            return pd.Series(date_times, index=series.index)

        # `datetime.date` instances become `pandas.Timestamp` instances because they are more compact/performant.
        # When all timestamps in a series/column share 00:00:00 for their time, pandas will display them as dates anyway.
        return pd.to_datetime(series, format="ISO8601")

    if is_time_type(data_type):
        return pd.to_timedelta(series)

    return series
