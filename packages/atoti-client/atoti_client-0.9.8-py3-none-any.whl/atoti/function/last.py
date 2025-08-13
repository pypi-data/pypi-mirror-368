from __future__ import annotations

from .._measure.first_last import FirstLast
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..level import Level


def last(
    measure: VariableMeasureConvertible,
    on: Level,
    /,
    *,
    partitioning: Level | None = None,
) -> MeasureDefinition:
    """Return a measure equal to the last value of the passed measure on the given level.

    Args:
        measure: The measure to shift.
        on: The level to shift on.
        partitioning: The level in the hierarchy at which to start over.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> from datetime import date
        >>> df = pd.DataFrame(
        ...     columns=["Date", "Quantity"],
        ...     data=[
        ...         (date(2019, 7, 2), 15),
        ...         (date(2019, 7, 1), 20),
        ...         (date(2019, 6, 1), 25),
        ...         (date(2019, 6, 2), 15),
        ...         (date(2019, 6, 30), 5),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, table_name="CumulativeTimePeriod")
        >>> cube = session.create_cube(table, mode="manual")
        >>> l, m = cube.levels, cube.measures
        >>> cube.create_date_hierarchy("Date", column=table["Date"])
        >>> m["Quantity.SUM"] = tt.agg.sum(table["Quantity"])
        >>> m["Quantity last day"] = tt.last(m["Quantity.SUM"], l["Day"])
        >>> m["Quantity last day of month"] = tt.last(
        ...     m["Quantity.SUM"], l["Day"], partitioning=l["Month"]
        ... )
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Quantity last day"],
        ...     m["Quantity last day of month"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Quantity.SUM Quantity last day Quantity last day of month
        Year  Month Day
        Total                     80                15
        2019                      80                15
              6                   45                15                          5
                    1             25                15                          5
                    2             15                15                          5
                    30             5                15                          5
              7                   35                15                         15
                    1             20                15                         15
                    2             15                15                         15

    """
    return FirstLast(
        _underlying_measure=convert_to_measure_definition(measure),
        _level_identifier=on._identifier,
        _mode="LAST",
        _partitioning=partitioning._identifier if partitioning is not None else None,
    )
