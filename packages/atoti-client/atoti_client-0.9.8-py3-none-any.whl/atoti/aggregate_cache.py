from collections.abc import Set as AbstractSet
from typing import Annotated, final

from pydantic import Field
from pydantic.dataclasses import dataclass

from ._identification import (
    Identifiable,
    MeasureIdentifier,
)
from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
@final
class AggregateCache:
    """Aggregate cache of a :class:`~atoti.Cube`.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> from dataclasses import replace
        >>> table = session.create_table("Example", data_types={"id": "int"})
        >>> cube = session.create_cube(table)
        >>> m = cube.measures

        There is a default cache:

        >>> cube.aggregate_cache
        AggregateCache(capacity=100, measures=None)

        Increasing the capacity and only caching :guilabel:`contributors.COUNT` aggregates:

        >>> cube.aggregate_cache = tt.AggregateCache(
        ...     capacity=200,
        ...     measures={m["contributors.COUNT"]},
        ... )
        >>> cube.aggregate_cache
        AggregateCache(capacity=200, measures=frozenset({m['contributors.COUNT']}))

        Changing back to caching all the measures:

        >>> cube.aggregate_cache = replace(cube.aggregate_cache, measures=None)
        >>> cube.aggregate_cache
        AggregateCache(capacity=200, measures=None)

        Disabling caching but keeping sharing enabled:

        >>> cube.aggregate_cache = replace(cube.aggregate_cache, capacity=0)
        >>> cube.aggregate_cache
        AggregateCache(capacity=0, measures=None)

        Disabling caching and sharing:

        >>> del cube.aggregate_cache
        >>> print(cube.aggregate_cache)
        None

    """

    capacity: Annotated[int, Field(ge=0)]
    """The capacity of the cache.

    * If greater than ``0``, this value corresponds to the maximum amount of ``{location: measure}`` pairs that the cache can hold.
    * If ``0``, caching is disabled but sharing stays enabled: concurrent queries will share their computed aggregates, but the aggregates will not be stored to be reused in later queries.
    """

    measures: (
        Annotated[AbstractSet[Identifiable[MeasureIdentifier]], Field(min_length=1)]
        | None
    ) = None
    """The measures to cache.

    This should typically be the measures that are known to be the most expensive to compute.

    If ``None``, all measures will be cached.
    """
