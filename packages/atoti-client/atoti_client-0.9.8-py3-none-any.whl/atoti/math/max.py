from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import MeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def max(  # noqa: A001
    *measures: MeasureConvertible,
) -> MeasureDefinition:
    """Return a measure equal to the maximum of the passed arguments.

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
        >>> m["max"] = tt.math.max(m["A.SUM"], m["B.SUM"])
        >>> cube.query(m["A.SUM"], m["B.SUM"], m["max"], levels=[l["City"]])
                   A.SUM  B.SUM    max
        City
        Berlin     15.00  10.00  15.00
        London     24.00  16.00  24.00
        New York  -27.00  15.00  15.00
        Paris        .00    .00    .00

    """
    if len(measures) <= 1:
        raise ValueError(
            "To find the maximum value of this measure on the levels it is expressed, use `atoti.agg.max()` instead.",
        )

    return CalculatedMeasure(
        Operator(
            "max",
            [convert_to_measure_definition(measure) for measure in measures],
        ),
    )
