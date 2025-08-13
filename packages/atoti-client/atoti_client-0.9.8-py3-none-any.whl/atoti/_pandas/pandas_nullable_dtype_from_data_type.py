from .._data_type import DataType
from .supported_pandas_nullable_dtype import SupportedPandasNullableDtype


def pandas_nullable_dtype_from_data_type(  # noqa: PLR0911
    data_type: DataType,
    /,
) -> SupportedPandasNullableDtype:
    match data_type:
        case "boolean":
            return "boolean"
        case "double":
            return "Float64"
        case "float":
            return "Float32"
        case "int":
            return "Int32"
        case "long":
            return "Int64"
        case "LocalDate" | "LocalDateTime" | "ZonedDateTime":
            return "datetime64[s]"
        case "String":
            return "string"
        case (
            "boolean[]"
            | "double[]"
            | "float[]"
            | "int[]"
            | "long[]"
            | "LocalTime"
            | "Object"
            | "Object[]"
            | "String[]"
        ):
            return "object"
