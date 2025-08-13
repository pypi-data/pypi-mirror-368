from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .identifier import Identifier

IdentifierT_co = TypeVar("IdentifierT_co", bound=Identifier, covariant=True)


class HasIdentifier(Generic[IdentifierT_co], ABC):
    @property
    @abstractmethod
    def _identifier(self) -> IdentifierT_co: ...
