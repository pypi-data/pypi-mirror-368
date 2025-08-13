from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable, Iterator, MutableSet, Set as AbstractSet
from typing import TypeVar, final

from typing_extensions import override

Item = TypeVar("Item")


class DelegatingMutableSet(MutableSet[Item]):
    @abstractmethod
    def _get_delegate(self) -> AbstractSet[Item]: ...

    @abstractmethod
    def _set_delegate(self, new_set: AbstractSet[Item], /) -> None: ...

    @final
    @override
    def __contains__(self, x: object) -> bool:
        return x in self._get_delegate()

    @final
    @override
    def __iter__(self) -> Iterator[Item]:
        return iter(self._get_delegate())

    @final
    @override
    def __len__(self) -> int:
        return len(self._get_delegate())

    @override
    def __repr__(self) -> str:
        # Converting to a `set` so that implementations of `_get_delegate()` returning a `frozenset` still repr as a regular `set`.
        return repr(set(self._get_delegate()))

    @final
    @override
    def add(self, value: Item) -> None:
        new_set = set(self._get_delegate())
        new_set.add(value)
        self._set_delegate(new_set)

    @final
    @override
    def clear(self) -> None:
        new_set: set[Item] = set()
        self._set_delegate(new_set)

    @final
    @override
    def discard(self, value: Item) -> None:
        new_set = set(self._get_delegate())
        new_set.discard(value)
        self._set_delegate(new_set)

    @final
    def update(self, *s: Iterable[Item]) -> None:  # pylint: disable=no-iterable
        new_set = set(self._get_delegate())
        new_set.update(*s)
        self._set_delegate(new_set)
