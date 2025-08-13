from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def floor(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return a measure equal to the largest integer <= to the passed measure.

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
        >>> m["⌊C⌋"] = tt.math.floor(m["C.SUM"])
        >>> cube.query(m["C.SUM"], m["⌊C⌋"], levels=[l["City"]])
                  C.SUM ⌊C⌋
        City
        Berlin    10.10  10
        London    20.50  20
        New York  30.70  30
        Paris       .00   0

    """
    return CalculatedMeasure(
        Operator("floor", [convert_to_measure_definition(measure)]),
    )
