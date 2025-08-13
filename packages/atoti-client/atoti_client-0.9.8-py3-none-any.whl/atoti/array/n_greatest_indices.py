from __future__ import annotations

from pydantic import PositiveInt

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def n_greatest_indices(
    measure: VariableMeasureConvertible,
    /,
    n: PositiveInt | VariableMeasureConvertible,
) -> MeasureDefinition:
    """Return an array measure containing the indices of the *n* greatest elements of the passed array measure.

    The indices in the returned array are sorted, so the first index corresponds to the greatest value and the last index to to the n-th greatest value.

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
        >>> m["Top 3 indices"] = tt.array.n_greatest_indices(m["PnL.SUM"], n=3)
        >>> cube.query(m["PnL.SUM"], m["Top 3 indices"])
                                  PnL.SUM         Top 3 indices
        0  doubleVector[10]{-20.163, ...}  intVector[3]{6, ...}

    """
    check_array_type(measure)
    return CalculatedMeasure(
        Operator(
            "n_greatest_indices",
            [convert_to_measure_definition(arg) for arg in [measure, n]],
        ),
    )
