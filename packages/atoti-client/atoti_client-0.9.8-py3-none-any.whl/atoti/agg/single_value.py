from typing import overload

from .._doc import doc
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..column import Column
from ..scope._scope import Scope
from ._agg import agg
from ._utils import SCOPE_DOC as _SCOPE_DOC


@overload
def single_value(operand: Column, /) -> MeasureDefinition: ...


@overload
def single_value(
    operand: VariableMeasureConvertible,
    /,
    *,
    scope: Scope,
) -> MeasureDefinition: ...


@doc(scope=_SCOPE_DOC, keys_argument="""{"Continent", "Country", "City"}""")
def single_value(
    operand: Column | VariableMeasureConvertible,
    /,
    *,
    scope: Scope | None = None,
) -> MeasureDefinition:
    """Return a measure equal to the value aggregation of the operand across the specified scope.

    If the value is the same for all members of the level the operand is being aggregated on, it will be propagated to the next level.

    ``None`` values are ignored: they will not prevent the propagation.

    Args:
        operand: The measure or table column to aggregate.
        {scope}

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["Continent", "Country", "City", "Price"],
        ...     data=[
        ...         ("Europe", "France", "Paris", 200.0),
        ...         ("Europe", "France", "Lyon", 200.0),
        ...         ("Europe", "UK", "London", 200.0),
        ...         ("Europe", "UK", "Manchester", 150.0),
        ...         ("Europe", "France", "Bordeaux", None),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys={keys_argument}, table_name="Example")
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> geography_level_names = ["Continent", "Country", "City"]
        >>> h["Geography"] = [table[name] for name in geography_level_names]
        >>> for name in geography_level_names:
        ...     del h[name]
        >>> m["Price.VALUE"] = tt.agg.single_value(table["Price"])
        >>> cube.query(
        ...     m["Price.VALUE"],
        ...     levels=[l["City"]],
        ...     include_empty_rows=True,
        ...     include_totals=True,
        ... )
                                     Price.VALUE
        Continent Country City
        Total
        Europe
                  France                  200.00
                          Bordeaux
                          Lyon            200.00
                          Paris           200.00
                  UK
                          London          200.00
                          Manchester      150.00

        * The :guilabel:`City` level is the most granular level so the members have the same value as in the input dataframe (including ``None`` for Bordeaux).
        * All the cities in France have the same price or ``None`` so the value is propagated to the :guilabel:`Country` level.
          The values in the UK cities are different so :guilabel:`Price.VALUE` is ``None``.
        * The cities in Europe have different values so the :guilabel:`Price.VALUE` is ``None`` at the :guilabel:`Continent` level.

    """
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="SINGLE_VALUE_NULLABLE", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
