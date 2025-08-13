from __future__ import annotations

from .._measure.boolean_measure import BooleanMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def isnan(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return a measure equal to ``True`` when the passed measure is ``NaN`` and to ``False`` otherwise.

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
        >>> m["Float division"] = m["A.SUM"] / m["B.SUM"]
        >>> m["Float division is NaN"] = tt.math.isnan(m["Float division"])
        >>> m["String is NaN"] = tt.math.isnan(tt.agg.single_value(table["City"]))
        >>> cube.query(
        ...     m["Float division"],
        ...     m["Float division is NaN"],
        ...     m["String is NaN"],
        ...     levels=[l["City"]],
        ... )
                 Float division Float division is NaN String is NaN
        City
        Berlin             1.50                 False         False
        London             1.50                 False         False
        New York          -1.80                 False         False
        Paris               NaN                  True         False

    """
    return BooleanMeasure("isNaN", (convert_to_measure_definition(measure),))
