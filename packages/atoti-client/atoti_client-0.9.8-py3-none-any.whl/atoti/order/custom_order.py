from __future__ import annotations

from typing import Annotated, final

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._collections import FrozenSequence
from .._constant import Scalar
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._base_order import BaseOrder


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class CustomOrder(BaseOrder):
    """Custom order with the given first elements.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     {
        ...         "Product": ["TV", "Smartphone", "Computer", "Screen"],
        ...         "Quantity": [12, 18, 50, 68],
        ...     }
        ... )
        >>> table = session.read_pandas(df, table_name="Products")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> cube.query(m["Quantity.SUM"], levels=[l["Product"]])
                   Quantity.SUM
        Product
        Computer             50
        Screen               68
        Smartphone           18
        TV                   12
        >>> l["Product"].order = tt.CustomOrder(first_elements=["TV", "Screen"])
        >>> cube.query(m["Quantity.SUM"], levels=[l["Product"]])
                   Quantity.SUM
        Product
        TV                   12
        Screen               68
        Computer             50
        Smartphone           18

    """

    first_elements: Annotated[FrozenSequence[Scalar], Field(min_length=1)]

    @property
    @override
    def _key(self) -> str:
        return "Custom"
