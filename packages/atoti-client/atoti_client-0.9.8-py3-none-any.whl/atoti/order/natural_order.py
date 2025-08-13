from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._base_order import BaseOrder


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class NaturalOrder(BaseOrder):
    """Ascending or descending natural order.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     {
        ...         "Date": ["2021-05-19", "2021-05-20"],
        ...         "Product": ["TV", "Smartphone"],
        ...         "Quantity": [12, 18],
        ...     }
        ... )
        >>> table = session.read_pandas(df, table_name="Sales")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> l["Date"].order == tt.NaturalOrder()
        True
        >>> cube.query(m["Quantity.SUM"], levels=[l["Date"]])
                   Quantity.SUM
        Date
        2021-05-19           12
        2021-05-20           18
        >>> l["Date"].order = tt.NaturalOrder(ascending=False)
        >>> cube.query(m["Quantity.SUM"], levels=[l["Date"]])
                   Quantity.SUM
        Date
        2021-05-20           18
        2021-05-19           12

    """

    ascending: bool = True

    @property
    @override
    def _key(self) -> str:
        return "NaturalOrder" if self.ascending else "ReverseOrder"
