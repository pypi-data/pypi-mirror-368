from __future__ import annotations

import math
import re
from collections.abc import Sequence
from datetime import date, datetime, time, timedelta, timezone
from typing import Annotated, TypeAlias, TypeVar, cast, final
from zoneinfo import ZoneInfo

from pydantic import BeforeValidator, PlainSerializer
from typing_extensions import TypedDict, TypeIs, assert_type

from ._data_type import (
    DataType,
    data_type_from_graphql as _data_type_from_graphql,
    data_type_to_graphql as _data_type_to_graphql,
)
from ._java import (
    JAVA_INT_RANGE,
    JAVA_MAX_LOCAL_DATE_STR,
    JAVA_MAX_LOCAL_DATE_TIME_STR,
    JAVA_MAX_UTC_ZONED_DATE_TIME_STR,
    JAVA_MIN_LOCAL_DATE_STR,
    JAVA_MIN_LOCAL_DATE_TIME_STR,
    JAVA_MIN_UTC_ZONED_DATE_TIME_STR,
    JAVA_NAN_STR,
    JAVA_NEGATIVE_INFINITY_STR,
    JAVA_POSITIVE_INFINITY_STR,
)
from ._pydantic import get_type_adapter


@final
class _SerializedConstant(TypedDict):
    dataType: str
    value: object


def _is_serialized_constant(value: object, /) -> TypeIs[_SerializedConstant]:
    return (
        isinstance(value, dict)
        and isinstance(value.get("dataType"), str)
        and "value" in value
    )


def _parse_data_type(data_type: str, /) -> DataType:
    # Nested import required to avoid circular import caused by custom `Constant` scalar.
    from ._graphql_client import (  # pylint: disable=nested-import
        DataType as GraphQlDataType,
    )

    return _data_type_from_graphql(GraphQlDataType[data_type])


def _parse_float(value: object, /) -> float:
    if isinstance(value, float):
        return value

    if isinstance(value, int):
        return float(value)

    if isinstance(value, str):
        if value == JAVA_NAN_STR:
            return math.nan
        if value == JAVA_NEGATIVE_INFINITY_STR:
            return -math.inf
        if value == JAVA_POSITIVE_INFINITY_STR:
            return math.inf

    raise ValueError(f"Unsupported value `{value}`.")


_DATE_TIME_PATTERN = re.compile(
    r"^(?P<date_time>[^[]+)(\[(?P<timezone_name>[^-+]+)((?P<timezone_offset>.+))?\])?$",
)


def _parse_datetime(value: str, /) -> datetime:
    match = _DATE_TIME_PATTERN.match(value)

    if not match:
        raise ValueError(
            f"`{value}` does not match expected format `{_DATE_TIME_PATTERN}`.",
        )

    datetime_value = get_type_adapter(datetime).validate_python(
        match.group("date_time"),
    )
    timezone_name = match.group("timezone_name")
    formatted_timezone_offset = match.group("timezone_offset")

    if formatted_timezone_offset:
        assert timezone_name
        timezone_offset = get_type_adapter(timedelta).validate_python(
            formatted_timezone_offset,
        )
        return datetime_value.replace(
            tzinfo=timezone(timezone_offset, timezone_name),
        )
    if timezone_name:
        return datetime_value.replace(tzinfo=ZoneInfo(timezone_name))
    return datetime_value


def _parse_json(  # noqa: C901, PLR0911, PLR0912, PLR0915
    value: object,
    /,
    *,
    data_type: DataType,
) -> Constant:
    match data_type:
        case "boolean":
            assert isinstance(value, bool)
            return value
        case "boolean[]":
            assert isinstance(value, Sequence)
            assert all(isinstance(element, bool) for element in value)
            return tuple(cast(Sequence[bool], value))
        case "double" | "float":
            return _parse_float(value)
        case "double[]" | "float[]":
            assert isinstance(value, Sequence)
            return tuple(_parse_float(element) for element in value)
        case "int":
            assert isinstance(value, int)
            assert value in JAVA_INT_RANGE
            return value
        case "int[]":
            assert isinstance(value, Sequence)
            assert all(
                isinstance(element, int) and (element in JAVA_INT_RANGE)
                for element in value
            )
            return tuple(cast(Sequence[int], value))
        case "LocalDate":
            assert isinstance(value, date | str)
            match value:
                case date():
                    return value
                case str():
                    if value == JAVA_MIN_LOCAL_DATE_STR:
                        return date.min
                    if value == JAVA_MAX_LOCAL_DATE_STR:
                        return date.max
                    return get_type_adapter(date).validate_python(value)
        case "LocalDateTime":
            assert isinstance(value, datetime | str)
            match value:
                case datetime():
                    return value
                case str():
                    if value == JAVA_MIN_LOCAL_DATE_TIME_STR:
                        return datetime.min  # noqa: DTZ901
                    if value == JAVA_MAX_LOCAL_DATE_TIME_STR:
                        return datetime.max  # noqa: DTZ901
                    return _parse_datetime(value)
        case "LocalTime":
            assert isinstance(value, str | time)
            match value:
                case str():
                    return get_type_adapter(time).validate_python(value)
                case time():
                    return value
        case "long":
            assert isinstance(value, int)
            return value
        case "long[]":
            assert isinstance(value, Sequence)
            assert all(isinstance(element, int) for element in value)
            return tuple(cast(Sequence[int], value))
        # Remove this case.
        # See https://github.com/activeviam/activepivot/blob/2ae2c77b47ca45d86e89ba12d76f00a301b310fe/atoti/patachou/server/server-base/src/main/java/io/atoti/server/base/private_/pivot/graphql/DataType.java#L12-L13.
        case "Object" | "Object[]":
            raise ValueError(f"Unsupported data type `{data_type}`.")
        case "String":
            assert isinstance(value, str)
            return value
        case "String[]":
            assert isinstance(value, Sequence)
            assert all(isinstance(element, str) for element in value)
            return tuple(cast(Sequence[str], value))
        case "ZonedDateTime":
            assert isinstance(value, datetime | str)
            match value:
                case datetime():
                    return value
                case str():
                    if value == JAVA_MIN_UTC_ZONED_DATE_TIME_STR:
                        return datetime.min.replace(tzinfo=timezone.utc)
                    if value == JAVA_MAX_UTC_ZONED_DATE_TIME_STR:
                        return datetime.max.replace(tzinfo=timezone.utc)
                    return _parse_datetime(value)


def _parse(value: _SerializedConstant, /) -> Constant:
    data_type = _parse_data_type(value["dataType"])
    return _parse_json(value["value"], data_type=data_type)


def _validate(value: object, /) -> object:
    return _parse(value) if _is_serialized_constant(value) else value


_Validator = BeforeValidator(_validate)


def data_type_of(value: Constant, /) -> DataType:  # noqa: C901, PLR0911, PLR0912
    match value:
        case bool():
            return "boolean"
        case int():
            return "int" if value in JAVA_INT_RANGE else "long"
        case float():
            return "double"
        case str():
            return "String"
        case datetime():
            return "LocalDateTime" if value.tzinfo is None else "ZonedDateTime"
        case date():
            return "LocalDate"
        case time():
            return "LocalTime"
        case Sequence():
            if not value:
                raise ValueError("Cannot infer data type from empty sequence.")
            match value[0]:
                case bool():
                    return "boolean[]"
                case int() | float():
                    data_types = {data_type_of(element) for element in value}
                    if data_types == {"int"}:
                        return "int[]"
                    if data_types == {"int", "long"}:
                        return "long[]"
                    return "double[]"
                case str():
                    return "String[]"


def _serialize_data_type(data_type: DataType, /) -> str:
    return _data_type_to_graphql(data_type).value


def _serialize_float(value: float, /) -> float | str:
    if math.isnan(value):
        return JAVA_NAN_STR
    if value == -math.inf:
        return JAVA_NEGATIVE_INFINITY_STR
    if value == math.inf:
        return JAVA_POSITIVE_INFINITY_STR
    return value


def _serialize_non_zoned_datetime(value: datetime, /) -> str:
    assert value.tzinfo is None
    if value == datetime.min:  # noqa: DTZ901
        return JAVA_MIN_LOCAL_DATE_TIME_STR
    if value == datetime.max:  # noqa: DTZ901
        return JAVA_MAX_LOCAL_DATE_TIME_STR
    return (
        value.strftime(r"%Y-%m-%dT%H:%M")
        if value.second == 0 and value.microsecond == 0
        else value.isoformat()
    )


def _serialize_datetime(value: datetime, /) -> str:
    if value.tzinfo is None:
        return _serialize_non_zoned_datetime(value)

    if value.tzinfo == ZoneInfo("UTC") or value.tzinfo == timezone.utc:
        return f"{_serialize_non_zoned_datetime(value.replace(tzinfo=None))}Z[UTC]"

    formatted_datetime_with_offset = value.isoformat()
    formatted_date, formatted_time_with_offset = formatted_datetime_with_offset.split(
        "T",
    )
    offset_sign = "+" if "+" in formatted_time_with_offset else "-"

    formatted_datetime_without_offset, formatted_offset = (
        formatted_time_with_offset.rsplit(
            offset_sign,
            maxsplit=1,
        )
    )
    trailing_zero_seconds = ":00"
    if formatted_datetime_without_offset.endswith(trailing_zero_seconds):
        formatted_datetime_without_offset = formatted_datetime_without_offset[
            : -len(trailing_zero_seconds)
        ]
        formatted_datetime_with_offset = f"{formatted_date}T{formatted_datetime_without_offset}{offset_sign}{formatted_offset}"

    formatted_timezone = str(value.tzinfo)

    if isinstance(value.tzinfo, timezone) and formatted_timezone in {
        "GMT",
        "UT",
        "UTC",
    }:
        formatted_timezone = f"{formatted_timezone}{offset_sign}{formatted_offset}"

    return f"{formatted_datetime_with_offset}[{formatted_timezone}]"


def json_from_constant(value: Constant, /) -> object:  # noqa: PLR0911
    match value:
        case float():
            return _serialize_float(value)
        case Sequence() if not isinstance(value, str):
            return tuple(
                _serialize_float(element) if isinstance(element, float) else element
                for element in value
            )
        case datetime():
            return _serialize_datetime(value)
        case date():
            if value == date.min:
                return JAVA_MIN_LOCAL_DATE_STR
            if value == date.max:
                return JAVA_MAX_LOCAL_DATE_STR
            return value.isoformat()
        case time():
            return (
                value.strftime(r"%H:%M")
                if value.second == 0 and value.microsecond == 0
                else value.isoformat()
            )
        case _:
            return value


def str_from_scalar(value: Scalar, /) -> str:
    json = json_from_constant(value)

    match json:
        case float() | int():
            return str(json)
        case str():
            return json
        case _:
            raise TypeError(f"Unexpected type `{type(json)}` for scalar `{value}`.")


def _serialize(
    value: Constant,  # pyright: ignore[reportUnknownParameterType]
    /,
) -> _SerializedConstant:
    data_type = data_type_of(value)
    json_value = json_from_constant(value)
    return {"dataType": _serialize_data_type(data_type), "value": json_value}


_Serializer = PlainSerializer(_serialize)

# Repeating the annotations for each variant so that they are always taken into account even if a parent type uses a single variant or a subset of all of them.
# For instance, `RelationalCondition[Identifier, Operator, Int | Float]` will only accept int or float targets while correctly parsing and serializing them.
Bool: TypeAlias = Annotated[bool, _Validator, _Serializer]
Int: TypeAlias = Annotated[int, _Validator, _Serializer]
Float: TypeAlias = Annotated[float, _Validator, _Serializer]
Date: TypeAlias = Annotated[date, _Validator, _Serializer]
Datetime: TypeAlias = Annotated[datetime, _Validator, _Serializer]
Time: TypeAlias = Annotated[time, _Validator, _Serializer]
Str: TypeAlias = Annotated[str, _Validator, _Serializer]

Scalar: TypeAlias = Bool | Int | Float | Date | Datetime | Time | Str

ScalarT_co = TypeVar("ScalarT_co", bound=Scalar, covariant=True)


def _create_array_validator(*element_types: type) -> BeforeValidator:
    def validate(value: object, /) -> object:
        if _is_serialized_constant(value):
            return _parse(value)
        if (
            isinstance(value, str)
            or not isinstance(value, Sequence)
            or not all(type(element) in element_types for element in value)
        ):
            raise ValueError(f"Expected a sequence of `{element_types}` elements.")
        return value

    return BeforeValidator(validate)


# Using `tuple` to enforce immutability.
# This is required to be able to do `set(constants)` without risking `TypeError: unhashable type`.
# This is not done with `FrozenSequence` because runtime type checking with `pydantic.validate_call()` is optional (it is disabled when `__debug__ == False`) so `Sequence`s such as `list`s are not always guaranteed to be converted to `tuple`s.
# In practice, most users will not disable runtime type checking so they will be able to pass `list`s or NumPy arrays and Pydantic will take care of the conversion to `tuple`s.
# Enforcing immutability of all constant values also avoids confusion: if `list`s were accepted, users could do `array = [1, 2]; m["array"] = array; array.append(3)` and expect `m["array"]` to be `[1, 2, 3]` while it would still be `[1, 2]`.
BoolArray = Annotated[tuple[bool, ...], _create_array_validator(bool), _Serializer]
IntArray = Annotated[tuple[int, ...], _create_array_validator(int), _Serializer]
FloatArray = Annotated[
    tuple[float, ...], _create_array_validator(int, float), _Serializer
]
StrArray = Annotated[tuple[str, ...], _create_array_validator(str), _Serializer]

Array: TypeAlias = BoolArray | IntArray | FloatArray | StrArray

Constant: TypeAlias = Scalar | Array

ConstantT_co = TypeVar("ConstantT_co", bound=Constant, covariant=True)


def is_array(value: Constant, /) -> TypeIs[Array]:
    return isinstance(value, Sequence) and not isinstance(value, str)


def is_scalar(value: Constant, /) -> TypeIs[Scalar]:
    if is_array(value):
        return False
    assert_type(value, Scalar)
    return True
