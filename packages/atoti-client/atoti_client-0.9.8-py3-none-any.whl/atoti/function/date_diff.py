from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition

_DateConstantOrVariableMeasureConvertible = date | datetime | VariableMeasureConvertible

_Unit = Literal["seconds", "minutes", "hours", "days", "weeks", "months", "years"]


def date_diff(
    from_date: _DateConstantOrVariableMeasureConvertible,
    to_date: _DateConstantOrVariableMeasureConvertible,
    /,
    *,
    unit: _Unit = "days",
) -> MeasureDefinition:
    """Return a measure equal to the difference between two dates.

    The measure evaluates to ``None`` if one of the dates is ``None``.

    Args:
        from_date: The starting date.
        to_date: The end date.
        unit: The difference unit.
            Seconds, minutes, and hours are only allowed if the dates contain time information.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> from datetime import date
        >>> df = pd.DataFrame(
        ...     columns=["From", "To"],
        ...     data=[
        ...         (date(2020, 1, 1), date(2020, 1, 2)),
        ...         (date(2020, 2, 1), date(2020, 2, 21)),
        ...         (date(2020, 3, 20), None),
        ...         (date(2020, 5, 15), date(2020, 4, 15)),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df, default_values={"To": None}, table_name="Example"
        ... )
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["To"] = tt.agg.single_value(table["To"])
        >>> m["Diff"] = tt.date_diff(l["From"], m["To"])
        >>> cube.query(m["To"], m["Diff"], levels=[l["From"]], include_empty_rows=True)
                            To Diff
        From
        2020-01-01  2020-01-02    1
        2020-02-01  2020-02-21   20
        2020-03-20
        2020-05-15  2020-04-15  -30

    """
    return CalculatedMeasure(
        Operator(
            "datediff",
            [
                convert_to_measure_definition(from_date),
                convert_to_measure_definition(to_date),
                unit,
            ],
        ),
    )
