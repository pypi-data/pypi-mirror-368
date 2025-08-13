from __future__ import annotations

from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..hierarchy import Hierarchy
from ..level import Level


def shift(
    measure: VariableMeasureConvertible,
    on: Hierarchy,
    /,
    *,
    offset: int = 1,
    partitioning: Level | None = None,
) -> MeasureDefinition:
    """Return a measure equal to the passed measure shifted to another member of the hierarchy.

    Args:
        measure: The measure to shift.
        on: The hierarchy to shift on.
        offset: The amount of members to shift by.
        partitioning: The level in the hierarchy at which to start the shift over.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["Country", "City", "Price"],
        ...     data=[
        ...         ("France", "Bordeaux", 1),
        ...         ("France", "Lyon", 2),
        ...         ("France", "Paris", 3),
        ...         ("Germany", "Berlin", 4),
        ...         ("Germany", "Frankfurt", 5),
        ...         ("Germany", "Munich", 6),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df,
        ...     table_name="Shift example",
        ... )
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> m["Shifted Price.SUM"] = tt.shift(m["Price.SUM"], h["City"], offset=2)
        >>> cube.query(
        ...     m["Price.SUM"],
        ...     m["Shifted Price.SUM"],
        ...     levels=[l["City"]],
        ...     include_totals=True,
        ... )
                  Price.SUM Shifted Price.SUM
        City
        Total            21
        Berlin            4                 5
        Bordeaux          1                 2
        Frankfurt         5                 6
        Lyon              2                 3
        Munich            6
        Paris             3

        >>> h["Location"] = [l["Country"], l["City"]]
        >>> m["Shifted Price.SUM"] = tt.shift(m["Price.SUM"], h["Location"], offset=1)
        >>> m["Shifted Price.SUM partitioned by Country"] = tt.shift(
        ...     m["Price.SUM"],
        ...     h["Location"],
        ...     offset=1,
        ...     partitioning=l["Location", "Country"],
        ... )
        >>> cube.query(
        ...     m["Price.SUM"],
        ...     m["Shifted Price.SUM"],
        ...     m["Shifted Price.SUM partitioned by Country"],
        ...     levels=[
        ...         l["Shift example", "Location", "Country"],
        ...         l["Shift example", "Location", "City"],
        ...     ],
        ...     include_totals=True,
        ... )
                          Price.SUM Shifted Price.SUM Shifted Price.SUM partitioned by Country
        Country City
        Total                    21
        France                    6                15
                Bordeaux          1                 2                                        2
                Lyon              2                 3                                        3
                Paris             3                 4
        Germany                  15
                Berlin            4                 5                                        5
                Frankfurt         5                 6                                        6
                Munich            6
    """
    return GenericMeasure(
        "LEAD_LAG",
        convert_to_measure_definition(measure),
        on._identifier._java_description,
        offset,
        partitioning._identifier._java_description
        if partitioning is not None
        else None,
    )
