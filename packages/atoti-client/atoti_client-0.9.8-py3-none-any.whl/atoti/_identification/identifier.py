from abc import ABC, abstractmethod

from typing_extensions import override


class Identifier(ABC):
    @override
    @abstractmethod
    def __repr__(self) -> str: ...
