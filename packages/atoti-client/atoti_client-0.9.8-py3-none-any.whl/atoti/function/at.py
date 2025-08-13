from __future__ import annotations

from typing import Literal, TypeAlias

from .._constant import Constant
from .._identification import LevelIdentifier
from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from .._operation import LogicalCondition, RelationalCondition, dict_from_condition

_CoordinatesLeafCondition: TypeAlias = RelationalCondition[
    LevelIdentifier, Literal["=="], Constant | LevelIdentifier
]
_CoordinatesCondition: TypeAlias = (
    _CoordinatesLeafCondition
    | LogicalCondition[_CoordinatesLeafCondition, Literal["&"]]
)


def at(
    measure: VariableMeasureConvertible,
    coordinates: _CoordinatesCondition,
    /,
) -> MeasureDefinition:
    """Return a measure equal to the passed measure at some other coordinates of the cube.

    Args:
        measure: The measure to take at other coordinates.
        coordinates: The condition specifying the coordinates at which to fetch the measure's value.
            It can only be a condition made of an equality test of a level with a single value or a combination of such conditions.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=[
        ...         "Country",
        ...         "City",
        ...         "Target Country",
        ...         "Target City",
        ...         "Quantity",
        ...     ],
        ...     data=[
        ...         ("Germany", "Berlin", "UK", "London", 15),
        ...         ("UK", "London", "Germany", "Berlin", 24),
        ...         ("USA", "New York", "UK", "London", 10),
        ...         ("USA", "New York", "France", "Paris", 3),
        ...         ("USA", "Seattle", "Germany", "Berlin", 3),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, table_name="At")
        >>> cube = session.create_cube(table, mode="manual")
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["Geography"] = [table["Country"], table["City"]]
        >>> h["Target Geography"] = [
        ...     table["Target Country"],
        ...     table["Target City"],
        ... ]
        >>> m["Quantity.SUM"] = tt.agg.sum(table["Quantity"])
        >>> # Using a constant matching an existing member of the level:
        >>> m["USA quantity"] = tt.at(m["Quantity.SUM"], l["Country"] == "USA")
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["USA quantity"],
        ...     levels=[l["Country"]],
        ... )
                Quantity.SUM USA quantity
        Country
        Germany           15           16
        UK                24           16
        USA               16           16
        >>> # Using another level whose current member the level on the left of the condition will be shifted to:
        >>> m["Target quantity"] = tt.at(
        ...     m["Quantity.SUM"],
        ...     (l["Country"] == l["Target Country"]) & (l["City"] == l["Target City"]),
        ... )
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Target quantity"],
        ...     levels=[l["City"], l["Target City"]],
        ... )
                                                    Quantity.SUM Target quantity
        Country City     Target Country Target City
        Germany Berlin   UK             London                15              24
        UK      London   Germany        Berlin                24              15
        USA     New York France         Paris                  3
                         UK             London                10              24
                Seattle  Germany        Berlin                 3              15

        Note that if the level on the right is not expressed, the shifting will not occur.

    """
    levels: list[str] = []
    target_levels: list[str | None] = []
    target_values: list[Constant | None] = []

    for subject, target in dict_from_condition(coordinates).items():
        levels.append(subject._java_description)

        match target:
            case LevelIdentifier():
                target_levels.append(target._java_description)
                target_values.append(None)
            case _:
                target_levels.append(None)
                target_values.append(target)

    return GenericMeasure(
        "LEVEL_AT",
        measure,
        levels,
        target_values,
        target_levels,
    )
