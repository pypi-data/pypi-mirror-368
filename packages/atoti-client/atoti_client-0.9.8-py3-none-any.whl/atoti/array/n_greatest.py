from __future__ import annotations

from pydantic import PositiveInt

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def n_greatest(
    measure: VariableMeasureConvertible,
    /,
    n: PositiveInt | VariableMeasureConvertible,
) -> MeasureDefinition:
    """Return an array measure containing the *n* greatest elements of the passed array measure.

    The values in the returned array are not sorted, use :func:`atoti.array.sort` to sort them.

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
        >>> m["Top 3"] = tt.array.n_greatest(m["PnL.SUM"], n=3)
        >>> cube.query(m["PnL.SUM"], m["Top 3"])
                                  PnL.SUM                                    Top 3
        0  doubleVector[10]{-20.163, ...}  doubleVector[3]{9.259999999999998, ...}

    """
    check_array_type(measure)
    return CalculatedMeasure(
        Operator(
            "n_greatest",
            [convert_to_measure_definition(arg) for arg in [measure, n]],
        ),
    )
