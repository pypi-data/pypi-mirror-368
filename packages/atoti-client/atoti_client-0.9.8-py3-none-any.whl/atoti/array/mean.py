from __future__ import annotations

from typing import cast, overload

from .._column_convertible import (
    ColumnOperation,
    VariableColumnConvertible,
    is_variable_column_convertible,
)
from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._create_function_operation import create_function_operation
from ._utils import check_array_type


@overload
def mean(value: VariableColumnConvertible, /) -> ColumnOperation: ...


@overload
def mean(value: VariableMeasureConvertible, /) -> MeasureDefinition: ...


def mean(
    value: VariableColumnConvertible | VariableMeasureConvertible,
    /,
) -> ColumnOperation | MeasureDefinition:
    """Return a measure equal to the mean of all the elements of the passed array measure.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> pnl_table = session.read_csv(
        ...     TEST_RESOURCES_PATH / "csv" / "pnl.csv",
        ...     array_separator=";",
        ...     keys={"Continent", "Country"},
        ...     table_name="PnL",
        ... )
        >>> cube = session.create_cube(pnl_table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Mean"] = tt.array.mean(m["PnL.SUM"])
        >>> m["Empty mean"] = tt.array.mean(m["PnL.SUM"][0:0])
        >>> cube.query(m["PnL.SUM"], m["Mean"], m["Empty mean"])
                                  PnL.SUM    Mean Empty mean
        0  doubleVector[10]{-20.163, ...}  -30.83        .00

    """
    if is_variable_column_convertible(value):
        create_function_operation(value, function_key="array_mean")

    value = cast(VariableMeasureConvertible, value)
    check_array_type(value)
    return CalculatedMeasure(
        Operator("mean_vector", [convert_to_measure_definition(value)]),
    )
