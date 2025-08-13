from __future__ import annotations

from pydantic import PositiveInt

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def nth_greatest(
    measure: VariableMeasureConvertible,
    /,
    n: PositiveInt | VariableMeasureConvertible,
) -> MeasureDefinition:
    """Return a measure equal to the *n*-th greatest element of the passed array measure.

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
        >>> m["3rd greatest"] = tt.array.nth_greatest(m["PnL.SUM"], n=3)
        >>> cube.query(m["PnL.SUM"], m["3rd greatest"])
                                  PnL.SUM 3rd greatest
        0  doubleVector[10]{-20.163, ...}         -.53

    """
    check_array_type(measure)
    return CalculatedMeasure(
        Operator(
            "nth_greatest",
            [convert_to_measure_definition(arg) for arg in [measure, n]],
        ),
    )
