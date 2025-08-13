from __future__ import annotations

from typing_extensions import TypeIs

from .._column_convertible import ColumnOperation, is_column_operation
from .._identification import ColumnIdentifier, HasIdentifier, LevelIdentifier
from .._udaf_operation import JavaFunctionOperation

LevelOrVariableColumnConvertible = (
    ColumnOperation
    | HasIdentifier[ColumnIdentifier | LevelIdentifier]
    | JavaFunctionOperation
)


def is_level_or_variable_column_convertible(
    value: object,
) -> TypeIs[LevelOrVariableColumnConvertible]:
    if isinstance(value, JavaFunctionOperation):
        return True

    if isinstance(value, HasIdentifier):
        return isinstance(value._identifier, ColumnIdentifier | LevelIdentifier)

    return is_column_operation(value)


BASIC_DOC = """Return a measure equal to the {value} of the passed measure across the specified scope.

    {args}

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["id", "Quantity", "Price", "Other"],
        ...     data=[
        ...         ("a1", 100, 12.5, 1),
        ...         ("a2", 10, 43, 2),
        ...         ("a3", 1000, 25.9, 2),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df,
        ...     keys=["id"],
        ...     table_name="Product",
        ... )
        >>> table.head().sort_index()
            Quantity  Price  Other
        id
        a1       100   12.5      1
        a2        10   43.0      2
        a3      1000   25.9      2
        >>> cube = session.create_cube(table)
        >>> m = cube.measures
{example}

"""

SCOPE_DOC = """
        scope: The :mod:`aggregation scope <atoti.scope>`.
    """

BASIC_ARGS_DOC = (
    """
    Args:
        operand: The measure or table column to aggregate.
"""
    + SCOPE_DOC
)

EXTREMUM_MEMBER_DOC = """Return a measure equal to the member {op}imizing the passed measure on the given level.

    When multiple members {op}imize the passed measure, the first one
    (according to the order of the given level) is returned.

    Args:
        measure: The measure to {op}imize.
        level: The level on which the {op}imizing member is searched for.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["Continent", "City", "Price"],
        ...     data=[
        ...         ("Europe", "Paris", 200.0),
        ...         ("Europe", "Berlin", 150.0),
        ...         ("Europe", "London", 240.0),
        ...         ("North America", "New York", 270.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df,
        ...     table_name="City price table",
        ... )
        >>> table.head()
               Continent      City  Price
        0         Europe     Paris  200.0
        1         Europe    Berlin  150.0
        2         Europe    London  240.0
        3  North America  New York  270.0
        >>> cube = session.create_cube(table, mode="manual")
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["Geography"] = [table["Continent"], table["City"]]
        >>> m["Price"] = tt.agg.single_value(table["Price"])
{example}

"""

QUANTILE_STD_AND_VAR_DOC_KWARGS = {
    "measure_or_operand": "operand",
    "what": "of the passed operand across the specified scope",
}
