from __future__ import annotations

from .._measure.first_last import FirstLast
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..level import Level


def first(
    measure: VariableMeasureConvertible,
    on: Level,
    /,
    *,
    partitioning: Level | None = None,
) -> MeasureDefinition:
    """Return a measure equal to the first value of the passed measure on the given level.

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
        >>> m["Quantity first day"] = tt.first(m["Quantity.SUM"], l["Day"])
        >>> m["Quantity first day of month"] = tt.first(
        ...     m["Quantity.SUM"], l["Day"], partitioning=l["Month"]
        ... )
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Quantity first day"],
        ...     m["Quantity first day of month"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Quantity.SUM Quantity first day Quantity first day of month
        Year  Month Day
        Total                     80                 25
        2019                      80                 25
              6                   45                 25                          25
                    1             25                 25                          25
                    2             15                 25                          25
                    30             5                 25                          25
              7                   35                 25                          20
                    1             20                 25                          20
                    2             15                 25                          20


    """
    return FirstLast(
        _underlying_measure=convert_to_measure_definition(measure),
        _level_identifier=on._identifier,
        _mode="FIRST",
        _partitioning=partitioning._identifier if partitioning is not None else None,
    )
