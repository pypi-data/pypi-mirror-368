from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def round(  # noqa: A001
    measure: VariableMeasureConvertible,
    /,
) -> MeasureDefinition:
    """Return a measure equal to the closest integer to the passed measure.

    Note:
        To change how a measure is displayed, use a :attr:`atoti.Measure.formatter` instead.

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
        >>> m["round(C)"] = tt.math.round(m["C.SUM"])
        >>> cube.query(m["C.SUM"], m["round(C)"], levels=[l["City"]])
                  C.SUM round(C)
        City
        Berlin    10.10       10
        London    20.50       21
        New York  30.70       31
        Paris       .00        0

    """
    return CalculatedMeasure(
        Operator("round", [convert_to_measure_definition(measure)]),
    )
