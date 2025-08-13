from typing import Literal, TypeAlias

SupportedPandasNullableDtype: TypeAlias = Literal[
    "boolean",
    "datetime64[s]",
    "datetime64[ms]",
    "datetime64[us]",
    "datetime64[ns]",
    "Float32",
    "Float64",
    "Int32",
    "Int64",
    "object",
    "string",
]
