from __future__ import annotations

from typing import overload

from .._doc import doc
from .._experimental import experimental
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..scope._scope import Scope
from ._agg import agg
from ._utils import SCOPE_DOC as _SCOPE_DOC, LevelOrVariableColumnConvertible


@overload
def distinct(operand: LevelOrVariableColumnConvertible, /) -> MeasureDefinition: ...


@overload
def distinct(
    operand: VariableMeasureConvertible,
    /,
    *,
    scope: Scope,
) -> MeasureDefinition: ...


@doc(scope=_SCOPE_DOC)
@experimental()
def distinct(
    operand: LevelOrVariableColumnConvertible | VariableMeasureConvertible,
    /,
    *,
    scope: Scope | None = None,
) -> MeasureDefinition:
    """Return an array measure equal to the distinct values of the passed measure across the specified scope.

    Warning:
        {experimental_feature}

    Args:
        operand: The measure or table column to aggregate.
        {scope}

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["ID", "City"],
        ...     data=[
        ...         (1, "Paris"),
        ...         (2, "London"),
        ...         (3, "New York"),
        ...         (4, "Paris"),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys={{"ID"}}, table_name="Example")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> with tt.experimental({{"agg.distinct"}}):
        ...     m["Distinct cities"] = tt.agg.distinct(table["City"])
        >>> m["Distinct cities"].formatter = "ARRAY[',']"
        >>> cube.query(m["Distinct cities"], levels=[l["City"]], include_totals=True)
                        Distinct cities
        City
        Total     New York,London,Paris
        London                   London
        New York               New York
        Paris                     Paris

    """
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="DISTINCT", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
