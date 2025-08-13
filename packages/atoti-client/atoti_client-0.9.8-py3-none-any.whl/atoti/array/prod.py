from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def prod(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return a measure equal to the product of all the elements of the passed array measure.

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
        >>> m["Product"] = tt.array.prod(m["PnL.SUM"])
        >>> m["Empty product"] = tt.array.prod(m["PnL.SUM"][0:0])
        >>> cube.query(m["PnL.SUM"], m["Product"], m["Empty product"])
                                  PnL.SUM             Product Empty product
        0  doubleVector[10]{-20.163, ...}  122,513,372,194.94          1.00

    """
    check_array_type(measure)
    return CalculatedMeasure(
        Operator("product_vector", [convert_to_measure_definition(measure)]),
    )
