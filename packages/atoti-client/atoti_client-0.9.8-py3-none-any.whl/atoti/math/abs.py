from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def abs(  # noqa: A001
    measure: VariableMeasureConvertible,
    /,
) -> MeasureDefinition:
    """Return a measure equal to the absolute value of the passed measure.

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
        >>> m["|A|"] = tt.math.abs(m["A.SUM"])
        >>> cube.query(m["A.SUM"], m["|A|"], levels=[l["City"]])
                   A.SUM    |A|
        City
        Berlin     15.00  15.00
        London     24.00  24.00
        New York  -27.00  27.00
        Paris        .00    .00

    """
    return CalculatedMeasure(Operator("abs", [convert_to_measure_definition(measure)]))
