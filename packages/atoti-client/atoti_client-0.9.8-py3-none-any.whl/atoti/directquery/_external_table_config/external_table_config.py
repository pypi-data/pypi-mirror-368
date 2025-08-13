from abc import ABC
from collections.abc import Set as AbstractSet
from typing import Generic

from pydantic.dataclasses import dataclass

from ..._collections import FrozenSequence
from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .._external_database_connection_config import (
    ExternalDatabaseConnectionConfigT,
)
from ._emulated_time_travel_table_config import EmulatedTimeTravelTableConfig


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ExternalTableConfig(Generic[ExternalDatabaseConnectionConfigT], ABC):
    clustering_columns: AbstractSet[str] = frozenset()
    """The names of the columns used for clustering.

    Feeding aggregate providers from an external database can result in very large queries to be run on this database.
    Clustering columns split up queries made by DirectQuery to the external database when feeding aggregate providers.
    """

    keys: AbstractSet[str] | FrozenSequence[str] | None = None
    """The columns that will become the table :attr:`~atoti.Table.keys`."""

    time_travel: EmulatedTimeTravelTableConfig | None = None
    """Optional configuration for emulated time-travel.

    :meta private:
    """
