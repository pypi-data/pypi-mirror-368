from abc import ABC

from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class CacheConfig(ABC):  # noqa: B024
    cache: bool = True
    """Whether to look for query results in the external database query cache."""

    @property
    def _cache_options(self) -> dict[str, str]:
        return {
            "USE_CACHE": str(self.cache).lower(),
        }
