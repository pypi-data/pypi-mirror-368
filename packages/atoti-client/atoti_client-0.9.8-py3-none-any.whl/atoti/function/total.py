from __future__ import annotations

from .._java import JAVA_INT_RANGE as _JAVA_INT_RANGE
from .._measure.parent_value import ParentValue
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..hierarchy import Hierarchy


def total(
    measure: VariableMeasureConvertible,
    /,
    *hierarchies: Hierarchy,
) -> MeasureDefinition:
    """Return a measure equal to the passed measure at the top level member on each given hierarchy.

    It ignores the filters on this hierarchy.

    If the hierarchy is not slicing, total is equal to the value for all the members.
    If the hierarchy is slicing, total is equal to the value on the first level.

    Args:
        measure: The measure to take the total of.
        hierarchies: The hierarchies on which to find the top-level member.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["Year", "Month", "Day", "Price"],
        ...     data=[
        ...         (2019, 7, 1, 15.0),
        ...         (2019, 7, 2, 20.0),
        ...         (2019, 6, 1, 25.0),
        ...         (2019, 6, 2, 15.0),
        ...         (2018, 7, 1, 5.0),
        ...         (2018, 7, 2, 10.0),
        ...         (2018, 6, 1, 15.0),
        ...         (2018, 6, 2, 5.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df, default_values={"Year": 0, "Month": 0, "Day": 0}, table_name="Total"
        ... )
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["Date"] = [table["Year"], table["Month"], table["Day"]]
        >>> m["Total(Price)"] = tt.total(m["Price.SUM"], h["Date"])
        >>> cube.query(
        ...     m["Price.SUM"],
        ...     m["Total(Price)"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Price.SUM Total(Price)
        Year  Month Day
        Total              110.00       110.00
        2018                35.00       110.00
              6             20.00       110.00
                    1       15.00       110.00
                    2        5.00       110.00
              7             15.00       110.00
                    1        5.00       110.00
                    2       10.00       110.00
        2019                75.00       110.00
              6             40.00       110.00
                    1       25.00       110.00
                    2       15.00       110.00
              7             35.00       110.00
                    1       15.00       110.00
                    2       20.00       110.00
        >>> h["Date"].slicing = True
        >>> cube.query(
        ...     m["Price.SUM"],
        ...     m["Total(Price)"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                       Price.SUM Total(Price)
        Year Month Day
        2018               35.00        35.00
             6             20.00        35.00
                   1       15.00        35.00
                   2        5.00        35.00
             7             15.00        35.00
                   1        5.00        35.00
                   2       10.00        35.00
        2019               75.00        75.00
             6             40.00        75.00
                   1       25.00        75.00
                   2       15.00        75.00
             7             35.00        75.00
                   1       15.00        75.00
                   2       20.00        75.00

    """
    measure = convert_to_measure_definition(measure)
    return ParentValue(
        _underlying_measure=measure,
        _degrees={
            hierarchy._identifier: _JAVA_INT_RANGE.stop - 1 for hierarchy in hierarchies
        },
        _total_value=measure,
        _apply_filters=False,
        _dense=False,
    )
