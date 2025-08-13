from __future__ import annotations

from collections.abc import Mapping

from .._measure.parent_value import ParentValue
from .._measure_convertible import MeasureConvertible, VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..hierarchy import Hierarchy


def parent_value(
    measure: VariableMeasureConvertible | str,
    /,
    *,
    degrees: Mapping[Hierarchy, int],
    apply_filters: bool = False,
    total_value: MeasureConvertible | None = None,
    dense: bool = False,
) -> MeasureDefinition:
    """Return a measure which values are equal to the values of the given *measure*, at a member that is located at a higher level on each of the specified hierarchy.

    This operation is also called drilling up a hierarchy.

    Args:
        measure: The measure from which the values are copied.
        degrees: The number of levels to go up to select the parent member along any given hierarchy.
        apply_filters: Whether or not the query filters on hierarchies specified in the *degrees* mapping must be applied when computing the value at the parent member.
        total_value: The value to return when the drill up went above the top level of all the hierarchies in the *degrees* mapping.
        dense: When ``True``, the parent value will be replicated on all members of the levels of the hierarchies in the *degrees* mapping, even those with no value for the given *measure*.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["Year", "Month", "Day", "Shop", "Quantity", "Other"],
        ...     data=[
        ...         (2019, 7, 1, "Shop1", 15, 245),
        ...         (2019, 7, 2, "Shop1", 20, 505),
        ...         (2019, 6, 1, "Shop2", 25, 115),
        ...         (2019, 6, 2, "Shop2", 15, 135),
        ...         (2018, 7, 1, "Shop1", 5, 55),
        ...         (2018, 7, 2, "Shop2", 10, 145),
        ...         (2018, 6, 1, "Shop1", 15, 145),
        ...         (2018, 6, 2, "Shop2", 5, 155),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df,
        ...     table_name="Parent Value",
        ...     default_values={"Year": 0, "Month": 0, "Day": 0},
        ... )
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["Date"] = [table["Year"], table["Month"], table["Day"]]
        >>> m["Degree 1"] = tt.parent_value(m["Quantity.SUM"], degrees={h["Date"]: 1})
        >>> m["Degree 2"] = tt.parent_value(m["Quantity.SUM"], degrees={h["Date"]: 2})
        >>> m["Degree 2 with Quantity total"] = tt.parent_value(
        ...     m["Quantity.SUM"],
        ...     degrees={h["Date"]: 2},
        ...     total_value=m["Quantity.SUM"],
        ... )
        >>> m["Degree 2 with Other total"] = tt.parent_value(
        ...     m["Quantity.SUM"],
        ...     degrees={h["Date"]: 2},
        ...     total_value=m["Other.SUM"],
        ... )
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Other.SUM"],
        ...     m["Degree 1"],
        ...     m["Degree 2"],
        ...     m["Degree 2 with Quantity total"],
        ...     m["Degree 2 with Other total"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Quantity.SUM Other.SUM Degree 1 Degree 2 Degree 2 with Quantity total Degree 2 with Other total
        Year  Month Day
        Total                    110     1,500                                            110                     1,500
        2018                      35       500      110                                   110                     1,500
              6                   20       300       35      110                          110                       110
                    1             15       145       20       35                           35                        35
                    2              5       155       20       35                           35                        35
              7                   15       200       35      110                          110                       110
                    1              5        55       15       35                           35                        35
                    2             10       145       15       35                           35                        35
        2019                      75     1,000      110                                   110                     1,500
              6                   40       250       75      110                          110                       110
                    1             25       115       40       75                           75                        75
                    2             15       135       40       75                           75                        75
              7                   35       750       75      110                          110                       110
                    1             15       245       35       75                           75                        75
                    2             20       505       35       75                           75                        75
        >>> h["Date"].slicing = True
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Other.SUM"],
        ...     m["Degree 1"],
        ...     m["Degree 2"],
        ...     m["Degree 2 with Quantity total"],
        ...     m["Degree 2 with Other total"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                       Quantity.SUM Other.SUM Degree 1 Degree 2 Degree 2 with Quantity total Degree 2 with Other total
        Year Month Day
        2018                     35       500                                             35                       500
             6                   20       300       35                                    35                       500
                   1             15       145       20       35                           35                        35
                   2              5       155       20       35                           35                        35
             7                   15       200       35                                    35                       500
                   1              5        55       15       35                           35                        35
                   2             10       145       15       35                           35                        35
        2019                     75     1,000                                             75                     1,000
             6                   40       250       75                                    75                     1,000
                   1             25       115       40       75                           75                        75
                   2             15       135       40       75                           75                        75
             7                   35       750       75                                    75                     1,000
                   1             15       245       35       75                           75                        75
                   2             20       505       35       75                           75                        75
        >>> h["Date"].slicing = False
        >>> m["Degree 1 with applied filter"] = tt.parent_value(
        ...     m["Quantity.SUM"], degrees={h["Date"]: 1}, apply_filters=True
        ... )
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Degree 1"],
        ...     m["Degree 1 with applied filter"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ...     filter=l["Year"] == "2018",
        ... )
                        Quantity.SUM Degree 1 Degree 1 with applied filter
        Year  Month Day
        Total                     35
        2018                      35      110                           35
              6                   20       35                           35
                    1             15       20                           20
                    2              5       20                           20
              7                   15       35                           35
                    1              5       15                           15
                    2             10       15                           15
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Degree 1"],
        ...     m["Degree 1 with applied filter"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ...     filter=l["Shop"] == "Shop1",
        ... )
                        Quantity.SUM Degree 1 Degree 1 with applied filter
        Year  Month Day
        Total                     55
        2018                      20       55                           55
              6                   15       20                           20
                    1             15       15                           15
              7                    5       20                           20
                    1              5        5                            5
        2019                      35       55                           55
              7                   35       35                           35
                    1             15       35                           35
                    2             20       35                           35

    See Also:
        :func:`atoti.total` to take the value at the top level member on each given hierarchy.

    """
    return ParentValue(
        _underlying_measure=measure
        if isinstance(measure, str)
        else convert_to_measure_definition(measure),
        _degrees={
            hierarchy._identifier: degree for hierarchy, degree in degrees.items()
        },
        _total_value=None
        if total_value is None
        else convert_to_measure_definition(total_value),
        _apply_filters=apply_filters,
        _dense=dense,
    )
