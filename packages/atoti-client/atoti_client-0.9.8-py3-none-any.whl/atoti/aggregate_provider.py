from __future__ import annotations

from collections.abc import Set as AbstractSet
from typing import Annotated, Literal, TypeAlias, final
from warnings import warn

from pydantic import Field
from pydantic.dataclasses import dataclass

from ._constant import Scalar
from ._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from ._identification import Identifiable, LevelIdentifier, MeasureIdentifier
from ._operation import LogicalCondition, MembershipCondition, RelationalCondition
from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._validate_hierarchy_unicity import validate_hierarchy_unicity

_AggregateProviderFilterMembershipConditionOperator: TypeAlias = Literal["in"]
_AggregateProviderFilterRelationalConditionOperator: TypeAlias = Literal["=="]
_AggregateProviderFilterLeafCondition: TypeAlias = (
    MembershipCondition[
        LevelIdentifier, _AggregateProviderFilterMembershipConditionOperator, Scalar
    ]
    | RelationalCondition[
        LevelIdentifier, _AggregateProviderFilterRelationalConditionOperator, Scalar
    ]
)
_AggregateProviderFilterCondition: TypeAlias = (
    _AggregateProviderFilterLeafCondition
    | LogicalCondition[_AggregateProviderFilterLeafCondition, Literal["&"]]
)
_AggregateProviderPluginKey: TypeAlias = Literal["bitmap", "leaf"]


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class AggregateProvider:
    """An aggregate provider pre-aggregates some measures up to certain levels.

    If a step of a query uses a subset of the aggregate provider's levels and measures, the provider will speed up the query.

    An aggregate provider uses additional memory to store the intermediate aggregates.
    The more levels and measures are added, the more memory it requires.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     {
        ...         "Seller": ["Seller_1", "Seller_1", "Seller_2", "Seller_2"],
        ...         "ProductId": ["aBk3", "ceJ4", "aBk3", "ceJ4"],
        ...         "Price": [2.5, 49.99, 3.0, 54.99],
        ...     }
        ... )
        >>> table = session.read_pandas(df, table_name="Seller")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> cube.aggregate_providers["Seller"] = tt.AggregateProvider(
        ...     filter=l["Seller"] == "Seller_1",
        ...     key="bitmap",
        ...     levels={l["Seller"]},
        ...     measures={m["Price.SUM"]},
        ...     partitioning="modulo4(Seller)",
        ... )
        >>> cube.aggregate_providers
        {'Seller': AggregateProvider(filter=l['Seller', 'Seller', 'Seller'] == 'Seller_1', key='bitmap', levels=frozenset({l['Seller', 'Seller', 'Seller']}), measures=frozenset({m['Price.SUM']}), partitioning='modulo4(Seller)')}

        Pre-aggregating all measures:

        >>> from dataclasses import replace
        >>> cube.aggregate_providers["Seller"] = replace(
        ...     cube.aggregate_providers["Seller"],
        ...     measures=None,
        ... )
        >>> cube.aggregate_providers["Seller"]
        AggregateProvider(filter=l['Seller', 'Seller', 'Seller'] == 'Seller_1', key='bitmap', levels=frozenset({l['Seller', 'Seller', 'Seller']}), measures=None, partitioning='modulo4(Seller)')

    """

    filter: _AggregateProviderFilterCondition | None = None
    """Only compute and provide aggregates matching this condition."""

    key: _AggregateProviderPluginKey = "leaf"
    """The key of the provider.

    The bitmap is generally faster but also takes more memory.
    """

    levels: (
        Annotated[
            AbstractSet[Identifiable[LevelIdentifier]],
            Field(min_length=1),
            # Uncomment in the next breaking release.
            # AfterValidator(validate_hierarchy_unicity),
        ]
        | None
    ) = None
    """The levels to build the provider on.

    If a passed level is part of a multilevel hierarchy, all shallower levels will be pre-aggregated too.
    If ``None``, all eligible levels will be pre-aggregated.
    """

    measures: (
        Annotated[
            AbstractSet[Identifiable[MeasureIdentifier]],
            Field(min_length=1),
        ]
        | None
    ) = None
    """The measures to build the provider on.

    If ``None``, all eligible measures will be pre-aggregated.
    """

    partitioning: str | None = None
    """The partitioning of the provider.

    Default to the partitioning of the cube's fact table.
    """

    def __post_init__(self) -> None:
        if self.levels:
            try:
                validate_hierarchy_unicity(self.levels)
            except ValueError as error:
                warn(
                    error.args[0],
                    category=_DEPRECATED_WARNING_CATEGORY,
                    stacklevel=2,
                )
