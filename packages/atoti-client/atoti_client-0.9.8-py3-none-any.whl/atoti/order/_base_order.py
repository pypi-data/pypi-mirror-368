from abc import ABC, abstractmethod

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class BaseOrder(ABC):
    """Base class for orders."""

    @property
    @abstractmethod
    def _key(self) -> str: ...
