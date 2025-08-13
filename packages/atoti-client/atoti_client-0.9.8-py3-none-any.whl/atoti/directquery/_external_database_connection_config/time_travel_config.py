from abc import ABC

from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class TimeTravelConfig(ABC):  # noqa: B024
    time_travel: bool = True
    """Whether to use time travel in queries."""

    @property
    def _time_travel_options(self) -> dict[str, str]:
        return {
            "ENABLE_TIME_TRAVEL": str(self.time_travel).lower(),
        }
