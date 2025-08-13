from __future__ import annotations

from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..hierarchy import Hierarchy


def rank(
    measure: VariableMeasureConvertible,
    hierarchy: Hierarchy,
    /,
    *,
    ascending: bool = True,
    apply_filters: bool = True,
) -> MeasureDefinition:
    """Return a measure equal to the rank of a hierarchy's members according to a reference measure.

    Members with equal values are further ranked using the level order.

    Args:
        measure: The measure on which the ranking is done.
        hierarchy: The hierarchy containing the members to rank.
        ascending: When set to ``False``, the 1st place goes to the member with greatest value.
        apply_filters: When ``True``, query filters on the given *hierarchy* will be applied before ranking members.
            When ``False``, query filters on the given *hierarchy* will be applied after the ranking, resulting in "holes" in the ranks.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["Year", "Month", "Day", "Quantity"],
        ...     data=[
        ...         (2000, 1, 1, 15),
        ...         (2000, 1, 2, 10),
        ...         (2000, 2, 1, 30),
        ...         (2000, 2, 2, 20),
        ...         (2000, 2, 5, 30),
        ...         (2000, 4, 4, 5),
        ...         (2000, 4, 5, 10),
        ...         (2020, 12, 6, 15),
        ...         (2020, 12, 7, 15),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df, table_name="Rank", default_values={"Year": 0, "Month": 0, "Day": 0}
        ... )
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["Date"] = [table["Year"], table["Month"], table["Day"]]
        >>> m["Rank"] = tt.rank(m["Quantity.SUM"], h["Date"])
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Rank"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Quantity.SUM Rank
        Year  Month Day
        Total                    150    1
        2000                     120    2
              1                   25    2
                    1             15    2
                    2             10    1
              2                   80    3
                    1             30    2
                    2             20    1
                    5             30    3
              4                   15    1
                    4              5    1
                    5             10    2
        2020                      30    1
              12                  30    1
                    6             15    1
                    7             15    2
        >>> m["Rank with filters not applied"] = tt.rank(
        ...     m["Quantity.SUM"], h["Date"], apply_filters=False
        ... )
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Rank"],
        ...     m["Rank with filters not applied"],
        ...     levels=[l["Month"]],
        ...     include_totals=True,
        ...     filter=l["Year"] == "2000",
        ... )
                    Quantity.SUM Rank Rank with filters not applied
        Year  Month
        Total                120    1                             1
        2000                 120    1                             2
              1               25    2                             2
              2               80    3                             3
              4               15    1                             1

        :guilabel:`2000-01-01` and :guilabel:`2000-01-05` have the same :guilabel:`Quantity.SUM` value so they're ranked according to `l["Day"].order`.
    """
    return GenericMeasure(
        "RANK",
        convert_to_measure_definition(measure),
        hierarchy._identifier._java_description,
        ascending,
        apply_filters,
    )
