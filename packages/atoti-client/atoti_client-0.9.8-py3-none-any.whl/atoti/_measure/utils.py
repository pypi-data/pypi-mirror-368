from collections.abc import Collection, Mapping
from typing import Any, cast

from py4j.java_gateway import JavaObject

from .._identification import (
    ColumnIdentifier,
    DimensionIdentifier,
    HasIdentifier,
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
    TableIdentifier,
)
from .._measure_convertible import MeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from .._operation import Condition, Operation
from .._py4j_client import Py4jClient
from .._py4j_client._utils import to_java_object, to_java_object_array


def get_measure_name(
    *,
    py4j_client: Py4jClient,
    measure: MeasureDefinition,
    cube_name: str,
) -> str:
    """Get the name of the measure from either a measure or its name."""
    return measure._distil(py4j_client=py4j_client, cube_name=cube_name).measure_name


def _convert_plugin_measure_arg(
    *,
    py4j_client: Py4jClient,
    arg: object,
) -> object:
    if isinstance(arg, HasIdentifier):
        return _extract_identifier(arg, py4j_client=py4j_client)

    # Recursively convert nested args.
    if isinstance(arg, tuple):
        return to_java_object_array(
            convert_plugin_measure_args(py4j_client=py4j_client, args=arg),
            gateway=py4j_client.gateway,
        )
    if isinstance(arg, list):
        return convert_plugin_measure_args(py4j_client=py4j_client, args=arg)
    if isinstance(arg, Mapping):
        return {
            _convert_plugin_measure_arg(
                py4j_client=py4j_client,
                arg=key,
            ): _convert_plugin_measure_arg(py4j_client=py4j_client, arg=value)
            for key, value in arg.items()
        }

    # Nothing smarter to do. Transform the argument to a java array.
    return to_java_object(arg, gateway=py4j_client.gateway)


def _extract_identifier(
    arg: HasIdentifier[Any], /, *, py4j_client: Py4jClient
) -> object:
    arg_identifier = arg._identifier

    if isinstance(arg_identifier, MeasureIdentifier):
        return arg_identifier.measure_name

    if isinstance(arg_identifier, ColumnIdentifier):
        return create_store_field(arg_identifier, py4j_client=py4j_client)

    if isinstance(arg_identifier, TableIdentifier):
        return arg_identifier.table_name

    if isinstance(arg_identifier, LevelIdentifier):
        return create_level_identifier(arg_identifier, py4j_client=py4j_client)

    if isinstance(arg_identifier, HierarchyIdentifier):
        return create_hierarchy_identifier(arg_identifier, py4j_client=py4j_client)

    if isinstance(arg_identifier, DimensionIdentifier):
        return arg_identifier.dimension_name

    raise TypeError(f"Unsupported identifier type: {type(arg_identifier)}")


def create_level_identifier(
    level: LevelIdentifier, /, *, py4j_client: Py4jClient
) -> JavaObject:
    jvm: Any = py4j_client.gateway.jvm
    extension_package = jvm.io.atoti.runtime.internal.extension.util
    return extension_package.IdentifierFactory.createLevelIdentifierFromDescription(
        level._java_description
    )


def create_hierarchy_identifier(
    hierarchy: HierarchyIdentifier, /, *, py4j_client: Py4jClient
) -> JavaObject:
    jvm: Any = py4j_client.gateway.jvm
    extension_package = jvm.io.atoti.runtime.internal.extension.util
    return extension_package.IdentifierFactory.createHierarchyIdentifierFromDescription(
        hierarchy._java_description
    )


def create_store_field(
    column: ColumnIdentifier, /, *, py4j_client: Py4jClient
) -> JavaObject:
    table_name = column.table_identifier.table_name
    column_name = column.column_name
    jvm: Any = py4j_client.gateway.jvm
    extension_package = jvm.io.atoti.runtime.internal.extension.util
    return extension_package.IdentifierFactory.createStoreField(table_name, column_name)


def convert_plugin_measure_args(
    *,
    py4j_client: Py4jClient,
    args: Collection[object],
) -> list[object]:
    """Convert arguments used for creating a measure in Java.

    The ``Measure`` arguments are replaced by their name, and other arguments are
    translated into Java-equivalent objects when necessary.
    """
    return [_convert_plugin_measure_arg(py4j_client=py4j_client, arg=a) for a in args]


def convert_measure_args(
    *,
    py4j_client: Py4jClient,
    cube_name: str,
    args: Collection[object],
) -> list[object]:
    """Convert arguments used for creating a measure in Java.

    The ``Measure`` arguments are replaced by their name, and other arguments are
    translated into Java-equivalent objects when necessary.
    """
    return [
        _convert_measure_arg(py4j_client=py4j_client, cube_name=cube_name, arg=a)
        for a in args
    ]


def _convert_measure_arg(  # noqa: PLR0911
    *,
    py4j_client: Py4jClient,
    cube_name: str,
    arg: object,
) -> object:
    if isinstance(arg, MeasureDefinition):
        return get_measure_name(
            py4j_client=py4j_client, measure=arg, cube_name=cube_name
        )

    if isinstance(arg, HasIdentifier) and isinstance(
        arg._identifier, MeasureIdentifier
    ):
        return arg._identifier.measure_name

    if isinstance(arg, (*Condition, Operation)):
        return _convert_measure_arg(
            py4j_client=py4j_client,
            cube_name=cube_name,
            arg=convert_to_measure_definition(cast(MeasureConvertible, arg)),
        )

    # Recursively convert nested args.
    if isinstance(arg, tuple):
        return to_java_object_array(
            convert_measure_args(
                py4j_client=py4j_client, cube_name=cube_name, args=arg
            ),
            gateway=py4j_client.gateway,
        )
    if isinstance(arg, list):
        return convert_measure_args(
            py4j_client=py4j_client, cube_name=cube_name, args=arg
        )
    if isinstance(arg, Mapping):
        return {
            _convert_measure_arg(
                py4j_client=py4j_client,
                cube_name=cube_name,
                arg=key,
            ): _convert_measure_arg(
                py4j_client=py4j_client, cube_name=cube_name, arg=value
            )
            for key, value in arg.items()
        }

    # Nothing smarter to do. Transform the argument to a java array.
    return to_java_object(arg, gateway=py4j_client.gateway)
