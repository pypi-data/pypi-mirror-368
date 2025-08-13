from typing import Literal

from .supported_pandas_nullable_dtype import SupportedPandasNullableDtype


def pandas_non_nullable_dtype_from_nullable_dtype(
    dtype: SupportedPandasNullableDtype,
    /,
) -> Literal[
    "bool",
    "datetime64[s]",
    "datetime64[ms]",
    "datetime64[us]",
    "datetime64[ns]",
    "float32",
    "float64",
    "int32",
    "int64",
    "object",
    "string",
]:
    match dtype:
        case "boolean":
            return "bool"
        case "Float32":
            return "float32"
        case "Float64":
            return "float64"
        case "Int32":
            return "int32"
        case "Int64":
            return "int64"
        case (
            "datetime64[s]"
            | "datetime64[ms]"
            | "datetime64[us]"
            | "datetime64[ns]"
            | "object"
            | "string"
        ):
            return dtype
