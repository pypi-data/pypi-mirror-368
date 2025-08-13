import datetime
from collections.abc import Collection, Mapping
from typing import Any, cast

import pandas as pd
from py4j.java_collections import (
    JavaArray,
    JavaList,
    JavaMap,
    JavaSet,
    ListConverter,
    SetConverter,
)
from py4j.java_gateway import CallbackServer, JavaClass, JavaGateway, JavaObject

from .._data_type import DataType
from .._identification import ColumnIdentifier


def _to_java_array(
    collection: Collection[Any],
    /,
    *,
    array_type: object,
    gateway: JavaGateway,
) -> JavaArray:
    array = cast(JavaArray, gateway.new_array(array_type, len(collection)))
    for index, element in enumerate(collection):
        array[index] = to_java_object(element, gateway=gateway)
    return array


def to_java_object_array(
    collection: Collection[Any],
    /,
    *,
    gateway: JavaGateway,
) -> JavaArray:
    return _to_java_array(collection, gateway=gateway, array_type=gateway.jvm.Object)


def to_java_string_array(
    collection: Collection[str],
    *,
    gateway: JavaGateway,
) -> JavaArray:
    return _to_java_array(collection, gateway=gateway, array_type=gateway.jvm.String)


def to_java_list(
    collection: Collection[Any],
    /,
    *,
    gateway: JavaGateway,
) -> JavaList:
    return cast(
        JavaList,
        ListConverter().convert(
            (to_java_object(element, gateway=gateway) for element in collection),
            gateway._gateway_client,
        ),
    )


def to_java_map(
    mapping: Mapping[Any, Any],
    /,
    *,
    gateway: JavaGateway,
) -> JavaMap:
    """Convert a Python mapping to a JavaMap preserving the order of the keys."""
    Map = JavaClass("java.util.LinkedHashMap", gateway._gateway_client)  # noqa: N806
    java_map = cast(JavaMap, Map())
    java_map.update(
        {
            to_java_object(key, gateway=gateway): to_java_object(value, gateway=gateway)
            for key, value in mapping.items()
        },
    )
    return java_map


def to_java_set(
    collection: Collection[Any],
    /,
    *,
    gateway: JavaGateway,
) -> JavaSet:
    return cast(
        JavaSet,
        SetConverter().convert(
            (to_java_object(element, gateway=gateway) for element in collection),
            gateway._gateway_client,
        ),
    )


def _to_java_date_or_time(
    date: datetime.date | datetime.datetime | datetime.time,
    *,
    gateway: JavaGateway,
) -> JavaObject:
    jvm: Any = gateway.jvm
    if isinstance(date, datetime.datetime):
        if not date.tzinfo:
            return jvm.java.time.LocalDateTime.parse(date.isoformat())
        return jvm.java.time.ZonedDateTime.parse(date.isoformat())
    if isinstance(date, datetime.time):
        if date.tzinfo:
            raise ValueError(
                f"Cannot handle time with timezone information: `{date.tzinfo}`.",
            )
        return jvm.java.time.LocalTime.of(
            date.hour,
            date.minute,
            date.second,
            date.microsecond * 1000,
        )
    return jvm.java.time.LocalDate.of(date.year, date.month, date.day)


def to_store_field(
    identifier: ColumnIdentifier,
    /,
    *,
    gateway: JavaGateway,
) -> JavaObject:
    jvm: Any = gateway.jvm
    StoreField: Any = jvm.com.activeviam.database.api.schema.StoreField  # noqa: N806
    return StoreField(identifier.table_identifier.table_name, identifier.column_name)


def _to_qfs_vector(
    collection: Collection[object],
    /,
    *,
    data_type: DataType | None = None,
    gateway: JavaGateway,
) -> JavaObject:
    jvm: Any = gateway.jvm
    vector_package = jvm.com.activeviam.tech.chunks.api.vectors
    if all(isinstance(x, int) for x in collection):
        if data_type == "int[]":
            array = _to_java_array(
                collection,
                gateway=gateway,
                array_type=gateway.jvm.int,
            )
            return vector_package.ArrayVectorUtils.intVector(array)
        array = _to_java_array(collection, gateway=gateway, array_type=gateway.jvm.long)
        return vector_package.ArrayVectorUtils.longVector(array)
    if all(isinstance(x, float | int) for x in collection):
        if data_type == "float[]":
            array = _to_java_array(
                [float(cast(int | float, x)) for x in collection],
                gateway=gateway,
                array_type=gateway.jvm.float,
            )
            return vector_package.ArrayVectorUtils.floatVector(array)
        array = _to_java_array(
            [float(cast(int | float, x)) for x in collection],
            gateway=gateway,
            array_type=gateway.jvm.double,
        )
        return vector_package.ArrayVectorUtils.doubleVector(array)
    array = to_java_object_array(collection, gateway=gateway)
    return vector_package.ArrayVectorUtils.objectVector(array)


def to_java_object(
    value: object,
    /,
    *,
    data_type: DataType | None = None,
    gateway: JavaGateway,
) -> Any:
    if isinstance(value, datetime.date | datetime.datetime | datetime.time):
        return _to_java_date_or_time(value, gateway=gateway)
    if isinstance(value, ColumnIdentifier):
        return to_store_field(value, gateway=gateway)
    if isinstance(value, tuple):
        return _to_qfs_vector(value, data_type=data_type, gateway=gateway)
    return value


def to_python_dict(
    java_map: JavaMap,
    /,
) -> dict[Any, Any]:
    return {key: java_map[key] for key in java_map}


def to_python_list(
    java_list: JavaList,
    /,
) -> list[Any]:
    return list(cast(Any, java_list).iterator())


def to_python_set(
    java_set: JavaSet,
    /,
) -> set[Any]:
    return set(cast(Any, java_set).iterator())


def to_python_object(
    java_object: JavaObject,
    /,
) -> object:
    _value: Any = java_object
    if _value.getClass().getName() in [
        "java.time.LocalDateTime",
        "java.time.ZonedDateTime",
    ]:
        return pd.to_datetime(
            _value.toString(),
        ).to_pydatetime()  # spell-checker: disable-line
    if _value.getClass().getName() == "java.time.LocalDate":
        return datetime.date.fromisoformat(_value.toString())
    if _value.getClass().getName() == "java.time.LocalTime":
        return datetime.time.fromisoformat(_value.toString())
    raise TypeError(f"Cannot convert object of type {type(java_object)} to Python.")


def patch_databricks_py4j() -> None:
    """Fix Databricks' monkey patching of py4j."""
    # The problematic version of Databricks outputs:
    # >>> print(CallbackServer.start.__qualname__)
    #  _daemonize_callback_server.<locals>.start
    #
    # More generally, it looks like most local monkey patches will have
    # the "locals" string in their name, so it's worth checking.

    if "locals" in CallbackServer.start.__qualname__:
        databricks_start = CallbackServer.start

        # Re-define the start function, adding back the missing code.
        def start(self: Any) -> None:
            databricks_start(self)

            if not hasattr(self, "_listening_address"):
                info = self.server_socket.getsockname()
                self._listening_address = info[0]
                self._listening_port = info[1]

        CallbackServer.start = start
