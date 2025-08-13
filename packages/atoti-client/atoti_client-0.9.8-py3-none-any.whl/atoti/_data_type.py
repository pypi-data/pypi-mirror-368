from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from typing_extensions import TypeIs

from ._typing import get_literal_args

if TYPE_CHECKING:
    # Nested import required to avoid circular import caused by custom `Constant` scalar.
    from ._graphql_client import (  # pylint: disable=nested-import
        DataType as GraphQlDataType,
    )


BooleanDataType = Literal["boolean"]
BooleanArrayDataType = Literal["boolean[]"]
DoubleArrayDataType = Literal["double[]"]
DoubleDataType = Literal["double"]
FloatArrayDataType = Literal["float[]"]
FloatDataType = Literal["float"]
IntArrayDataType = Literal["int[]"]
IntDataType = Literal["int"]
LocalDateDataType = Literal["LocalDate"]
LocalDateTimeDataType = Literal["LocalDateTime"]
LocalTimeDataType = Literal["LocalTime"]
LongArrayDataType = Literal["long[]"]
LongDataType = Literal["long"]
ObjectArrayDataType = Literal["Object[]"]
ObjectDataType = Literal["Object"]
StringDataType = Literal["String"]
StringArrayDataType = Literal["String[]"]
ZonedDateTimeDataType = Literal["ZonedDateTime"]


# Order matters: a type can be widened to the previous type.
NumericDataType = Literal[DoubleDataType, FloatDataType, LongDataType, IntDataType]
_NUMERIC_DATA_TYPE_ARGS = get_literal_args(NumericDataType)

PrimitiveDataType = Literal[BooleanDataType, NumericDataType]
_PRIMITIVE_DATA_TYPE_ARGS = get_literal_args(PrimitiveDataType)

# Order matters: a type can be widened to the previous type.
DateDataType = Literal[
    ZonedDateTimeDataType,
    LocalDateTimeDataType,
    LocalDateDataType,
]
_DATE_DATA_TYPE_ARGS = get_literal_args(DateDataType)

TimeDataType = Literal[LocalTimeDataType]
_TIME_DATA_TYPE_ARGS = get_literal_args(TimeDataType)

TemporalDataType = Literal[DateDataType, TimeDataType]
_TEMPORAL_DATA_TYPE_ARGS = get_literal_args(TemporalDataType)

# Must be ordered as `NumericDataType`.
NumericArrayDataType = Literal[
    DoubleArrayDataType,
    FloatArrayDataType,
    LongArrayDataType,
    IntArrayDataType,
]
_NUMERIC_ARRAY_DATA_TYPE_ARGS = get_literal_args(NumericArrayDataType)

ArrayDataType = Literal[
    BooleanArrayDataType,
    NumericArrayDataType,
    ObjectArrayDataType,
    StringArrayDataType,
]
_ARRAY_DATA_TYPE_ARGS = get_literal_args(ArrayDataType)

# Built from the hierarchy of data types.
# Should contain all the data types.
_AggregatedDataType = Literal[
    PrimitiveDataType,
    ArrayDataType,
    TemporalDataType,
    ObjectDataType,
    StringDataType,
]

# Flat list of data types to make them easier to read in the API Reference/IDEs/Type checkers.
DataType = Literal[
    "boolean",
    "boolean[]",
    "double",
    "double[]",
    "float",
    "float[]",
    "int",
    "int[]",
    "LocalDate",
    "LocalDateTime",
    "LocalTime",
    "long",
    "long[]",
    # Remove `Object` and `Object[]`.
    # See https://github.com/activeviam/activepivot/blob/2ae2c77b47ca45d86e89ba12d76f00a301b310fe/atoti/patachou/server/server-base/src/main/java/io/atoti/server/base/private_/pivot/graphql/DataType.java#L12-L13.
    "Object",
    "Object[]",
    "String",
    "String[]",
    "ZonedDateTime",
]
_DATA_TYPE_ARGS = get_literal_args(DataType)

_ARRAY_SUFFIX = "[]"


def parse_data_type(value: str, /) -> DataType:
    value = value.lower()

    try:
        return next(
            cast(Any, data_type)
            for data_type in _DATA_TYPE_ARGS
            if value == cast(str, data_type).lower()
        )
    except StopIteration as error:
        raise TypeError(f"""Expected a data type but got "{value}".""") from error


def is_array_type(data_type: DataType, /) -> TypeIs[ArrayDataType]:
    return data_type in _ARRAY_DATA_TYPE_ARGS


def to_array_type(data_type: DataType, /) -> ArrayDataType:
    data_type = parse_data_type(f"{data_type}{_ARRAY_SUFFIX}")
    if not is_array_type(data_type):
        raise TypeError(f"Expected {data_type} to be an array type.")
    return data_type


def is_date_type(data_type: DataType, /) -> TypeIs[DateDataType]:
    return data_type in _DATE_DATA_TYPE_ARGS


def is_time_type(data_type: DataType, /) -> TypeIs[TimeDataType]:
    return data_type in _TIME_DATA_TYPE_ARGS


def is_temporal_type(data_type: DataType, /) -> TypeIs[TemporalDataType]:
    return data_type in _TEMPORAL_DATA_TYPE_ARGS


def is_numeric_type(data_type: DataType, /) -> TypeIs[NumericDataType]:
    return data_type in _NUMERIC_DATA_TYPE_ARGS


def is_numeric_array_type(data_type: DataType, /) -> TypeIs[NumericArrayDataType]:
    return data_type in _NUMERIC_ARRAY_DATA_TYPE_ARGS


def get_numeric_array_element_type(
    data_type: NumericArrayDataType,
    /,
) -> NumericDataType:
    return cast(NumericDataType, parse_data_type(data_type[: -len(_ARRAY_SUFFIX)]))


def is_primitive_type(data_type: DataType, /) -> TypeIs[PrimitiveDataType]:
    return data_type in _PRIMITIVE_DATA_TYPE_ARGS


def data_type_from_graphql(data_type: GraphQlDataType, /) -> DataType:  # noqa: C901, PLR0911, PLR0912
    # Nested import required to avoid circular import caused by custom `Constant` scalar.
    from ._graphql_client import (  # pylint: disable=nested-import
        DataType as GraphQlDataType,
    )

    # Using `match` instead of a `dict` to ensure that type checkers verify exhaustiveness.
    match data_type:
        case GraphQlDataType.BOOLEAN:
            return "boolean"
        case GraphQlDataType.BOOLEAN_ARRAY:
            return "boolean[]"
        case GraphQlDataType.DOUBLE:
            return "double"
        case GraphQlDataType.DOUBLE_ARRAY:
            return "double[]"
        case GraphQlDataType.FLOAT:
            return "float"
        case GraphQlDataType.FLOAT_ARRAY:
            return "float[]"
        case GraphQlDataType.INT:
            return "int"
        case GraphQlDataType.INT_ARRAY:
            return "int[]"
        case GraphQlDataType.LOCAL_DATE:
            return "LocalDate"
        case GraphQlDataType.LOCAL_DATE_TIME:
            return "LocalDateTime"
        case GraphQlDataType.LOCAL_TIME:
            return "LocalTime"
        case GraphQlDataType.LONG:
            return "long"
        case GraphQlDataType.LONG_ARRAY:
            return "long[]"
        case GraphQlDataType.STRING:
            return "String"
        case GraphQlDataType.STRING_ARRAY:
            return "String[]"
        case GraphQlDataType.ZONED_DATE_TIME:
            return "ZonedDateTime"


def data_type_to_graphql(data_type: DataType, /) -> GraphQlDataType:  # noqa: C901, PLR0911, PLR0912
    # Nested import required to avoid circular import caused by custom `Constant` scalar.
    from ._graphql_client import (  # pylint: disable=nested-import
        DataType as GraphQlDataType,
    )

    # Using `match` instead of a `dict` to ensure that type checkers verify exhaustiveness.
    match data_type:
        case "boolean":
            return GraphQlDataType.BOOLEAN
        case "boolean[]":
            return GraphQlDataType.BOOLEAN_ARRAY
        case "double":
            return GraphQlDataType.DOUBLE
        case "double[]":
            return GraphQlDataType.DOUBLE_ARRAY
        case "float":
            return GraphQlDataType.FLOAT
        case "float[]":
            return GraphQlDataType.FLOAT_ARRAY
        case "int":
            return GraphQlDataType.INT
        case "int[]":
            return GraphQlDataType.INT_ARRAY
        case "LocalDate":
            return GraphQlDataType.LOCAL_DATE
        case "LocalDateTime":
            return GraphQlDataType.LOCAL_DATE_TIME
        case "LocalTime":
            return GraphQlDataType.LOCAL_TIME
        case "long":
            return GraphQlDataType.LONG
        case "long[]":
            return GraphQlDataType.LONG_ARRAY
        case "Object" | "Object[]":
            raise ValueError(f"`{data_type}` is not supported by GraphQL API.")
        case "String":
            return GraphQlDataType.STRING
        case "String[]":
            return GraphQlDataType.STRING_ARRAY
        case "ZonedDateTime":
            return GraphQlDataType.ZONED_DATE_TIME
