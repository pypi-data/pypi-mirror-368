from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def len(  # noqa: A001
    measure: VariableMeasureConvertible,
    /,
) -> MeasureDefinition:
    """Return a measure equal to the number of elements of the passed array measure.

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
        >>> m["Length"] = tt.array.len(m["PnL.SUM"])
        >>> cube.query(m["PnL.SUM"], m["Length"])
                                  PnL.SUM Length
        0  doubleVector[10]{-20.163, ...}     10

    """
    check_array_type(measure)
    return CalculatedMeasure(
        Operator("vector_length", [convert_to_measure_definition(measure)]),
    )
