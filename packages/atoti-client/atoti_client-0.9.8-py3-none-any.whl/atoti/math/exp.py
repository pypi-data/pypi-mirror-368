from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def exp(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return a measure equal to the exponential value of the passed measure.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["City", "A", "B", "C", "D"],
        ...     data=[
        ...         ("Berlin", 15.0, 10.0, 10.1, 1.0),
        ...         ("London", 24.0, 16.0, 20.5, 3.14),
        ...         ("New York", -27.0, 15.0, 30.7, 10.0),
        ...         ("Paris", 0.0, 0.0, 0.0, 0.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys={"City"}, table_name="Math")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["exp(D)"] = tt.math.exp(m["D.SUM"])
        >>> cube.query(m["D.SUM"], m["exp(D)"], levels=[l["City"]])
                  D.SUM     exp(D)
        City
        Berlin     1.00       2.72
        London     3.14      23.10
        New York  10.00  22,026.47
        Paris       .00       1.00

    """
    return CalculatedMeasure(Operator("exp", [convert_to_measure_definition(measure)]))
