from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Annotated, Literal, TypeVar

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ..._typing import Duration


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ExternalDatabaseConnectionConfig(ABC):
    column_clustered_queries: Literal["all", "feeding"] = "feeding"
    """Control which queries will use clustering columns."""

    feeding_query_timeout: Duration = timedelta(hours=1)
    """Timeout for queries performed on the external database during feeding phases.

    The feeding phases are:

    * the initial load to feed :attr:`~atoti.Cube.aggregate_providers` and :attr:`~atoti.Cube.hierarchies`;
    * the refresh operations.
    """

    lookup_mode: Literal["allow", "warn", "deny"] = "warn"
    """Whether lookup queries on the external database are allowed.

    Lookup can be very slow and expensive as the database may not enforce primary keys.
    """

    max_sub_queries: Annotated[int, Field(gt=0)] = 500
    """Maximum number of sub queries performed when splitting a query into multi-step queries."""

    query_timeout: Duration = timedelta(minutes=5)
    """Timeout for queries performed on the external database outside feeding phases."""

    @property
    @abstractmethod
    def _database_key(self) -> str: ...

    @property
    def _options(self) -> dict[str, str]:
        use_clustering_fields: str

        match self.column_clustered_queries:
            case "all":
                use_clustering_fields = "ALWAYS"
            case "feeding":
                use_clustering_fields = "FEEDING"

        return {
            "EXTERNAL_DATABASE_FEEDING_QUERY_TIMEOUT": str(
                int(self.feeding_query_timeout.total_seconds()),
            ),
            "EXTERNAL_DATABASE_QUERY_TIMEOUT": str(
                int(self.query_timeout.total_seconds()),
            ),
            "GET_BY_KEY_QUERY_BEHAVIOR": self.lookup_mode.upper(),
            "MAX_SUB_QUERIES_ALLOWED_IN_MULTI_STEP_QUERY": str(self.max_sub_queries),
            "USE_CLUSTERING_FIELDS": use_clustering_fields,
        }

    @property
    @abstractmethod
    def _password(self) -> str | None: ...

    @property
    @abstractmethod
    def _url(self) -> str | None: ...


ExternalDatabaseConnectionConfigT = TypeVar(
    "ExternalDatabaseConnectionConfigT",
    bound=ExternalDatabaseConnectionConfig,
)
