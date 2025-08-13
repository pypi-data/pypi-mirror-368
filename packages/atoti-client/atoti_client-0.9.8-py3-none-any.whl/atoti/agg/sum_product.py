from __future__ import annotations

from typing import overload

from .._doc import doc
from .._measure.sum_product_measure import (
    SumProductEncapsulationMeasure,
    SumProductFieldsMeasure,
)
from .._measure_convertible import MeasureConvertible
from .._measure_definition import MeasureDefinition
from ..column import Column
from ..scope._scope import Scope
from ._agg import agg
from ._utils import SCOPE_DOC as _SCOPE_DOC


@overload
def sum_product(*factors: Column) -> MeasureDefinition: ...


@overload
def sum_product(*factors: MeasureConvertible, scope: Scope) -> MeasureDefinition: ...


@doc(scope=_SCOPE_DOC)
def sum_product(
    *factors: Column | MeasureConvertible,
    scope: Scope | None = None,
) -> MeasureDefinition:
    """Return a measure equal to the sum product aggregation of the passed factors across the specified scope.

    Args:
        factors: The factors to multiply together and then aggregate as a sum.
        {scope}

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> from datetime import date
        >>> df = pd.DataFrame(
        ...     columns=["Date", "Category", "Price", "Quantity", "Array"],
        ...     data=[
        ...         (date(2020, 1, 1), "TV", 300.0, 5, [10.0, 15.0]),
        ...         (date(2020, 1, 2), "TV", 200.0, 1, [5.0, 15.0]),
        ...         (date(2020, 1, 1), "Computer", 900.0, 2, [2.0, 3.0]),
        ...         (date(2020, 1, 2), "Computer", 800.0, 3, [10.0, 20.0]),
        ...         (date(2020, 1, 1), "TV", 500.0, 2, [3.0, 10.0]),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df,
        ...     table_name="Date",
        ... )
        >>> table.head().sort_values(["Category", "Date"]).reset_index(drop=True)
                Date  Category  Price  Quantity         Array
        0 2020-01-01  Computer  900.0         2    [2.0, 3.0]
        1 2020-01-02  Computer  800.0         3  [10.0, 20.0]
        2 2020-01-01        TV  300.0         5  [10.0, 15.0]
        3 2020-01-01        TV  500.0         2   [3.0, 10.0]
        4 2020-01-02        TV  200.0         1   [5.0, 15.0]
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> m["turnover"] = tt.agg.sum_product(table["Price"], table["Quantity"])
        >>> cube.query(m["turnover"], levels=[l["Category"]])
                  turnover
        Category
        Computer  4,200.00
        TV        2,700.00
        >>> m["array sum product"] = tt.agg.sum_product(table["Price"], table["Array"])
        >>> cube.query(m["array sum product"])
                       array sum product
        0  doubleVector[2]{{15300.0, ...}}
    """
    if len(factors) < 1:
        raise ValueError("At least one factor is needed.")

    columns = [factor for factor in factors if isinstance(factor, Column)]

    if len(columns) == len(factors):
        if scope is not None:
            raise TypeError("Cannot aggregate columns with a scope.")

        return SumProductFieldsMeasure(_factors=columns)

    measures = [factor for factor in factors if not isinstance(factor, Column)]

    if len(measures) != len(factors):
        raise ValueError(
            "Cannot aggregate a mix of measures and table columns or operations. Consider converting all the factors to measures.",
        )

    return agg(
        SumProductEncapsulationMeasure(_factors=measures),
        plugin_key="ATOTI_SUM_PRODUCT",
        # The type checkers cannot see that the `@overload` above ensure that this call is valid.
        scope=scope,  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    )
