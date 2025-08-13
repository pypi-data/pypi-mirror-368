from __future__ import annotations

from .._measure_convertible import MeasureOperation, VariableMeasureConvertible
from .._measure_definition import convert_to_measure_definition


def sqrt(measure: VariableMeasureConvertible, /) -> MeasureOperation:
    """Return a measure equal to the square root of the passed measure.

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
        >>> m["√B"] = tt.math.sqrt(m["B.SUM"])
        >>> cube.query(m["B.SUM"], m["√B"], levels=[l["City"]])
                  B.SUM    √B
        City
        Berlin    10.00  3.16
        London    16.00  4.00
        New York  15.00  3.87
        Paris       .00   .00

    """
    return convert_to_measure_definition(measure) ** 0.5
