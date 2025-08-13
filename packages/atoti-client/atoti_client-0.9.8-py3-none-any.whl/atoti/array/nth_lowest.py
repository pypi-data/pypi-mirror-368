from __future__ import annotations

from pydantic import PositiveInt

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def nth_lowest(
    measure: VariableMeasureConvertible,
    /,
    n: PositiveInt | VariableMeasureConvertible,
) -> MeasureDefinition:
    """Return a measure equal to the *n*-th lowest element of the passed array measure.

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
        >>> m["3rd lowest"] = tt.array.nth_lowest(m["PnL.SUM"], n=3)
        >>> cube.query(m["PnL.SUM"], m["3rd lowest"])
                                  PnL.SUM 3rd lowest
        0  doubleVector[10]{-20.163, ...}     -57.51

    """
    check_array_type(measure)
    return CalculatedMeasure(
        Operator(
            "nth_lowest",
            [convert_to_measure_definition(arg) for arg in [measure, n]],
        ),
    )
