from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def log(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return a measure equal to the natural logarithm (base *e*) of the passed measure.

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
        >>> m["log(D)"] = tt.math.log(m["D.SUM"])
        >>> cube.query(m["D.SUM"], m["log(D)"], levels=[l["City"]])
                  D.SUM log(D)
        City
        Berlin     1.00    .00
        London     3.14   1.14
        New York  10.00   2.30
        Paris       .00     -∞

    """
    return CalculatedMeasure(Operator("log", [convert_to_measure_definition(measure)]))
