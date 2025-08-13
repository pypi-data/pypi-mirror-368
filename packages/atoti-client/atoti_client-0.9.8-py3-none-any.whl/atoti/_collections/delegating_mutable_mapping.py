from __future__ import annotations

from abc import ABC
from collections.abc import Mapping, MutableMapping, Sequence, Set as AbstractSet
from typing import overload

from typing_extensions import override

from .delegating_converting_mapping import _DelegatingConvertingMapping
from .supports_unchecked_mapping_lookup import UnambiguousKey as Key, Value


class DelegatingMutableMapping(
    _DelegatingConvertingMapping[Key, Key, Value, Value],
    MutableMapping[Key, Value],
    ABC,
):
    @overload  # type: ignore[misc,override]
    def update(
        self,
        other: Mapping[Key, Value],
        /,
        **kwargs: Value,
    ) -> None: ...

    @overload
    def update(
        self,
        # Using `Sequence | AbstractSet` instead of `Iterable` or `Collection` to have Pydantic validate `other` without converting it to a `ValidatorIterator`.
        other: Sequence[tuple[Key, Value]] | AbstractSet[tuple[Key, Value]],
        /,
        **kwargs: Value,
    ) -> None: ...

    @overload
    def update(self, **kwargs: Value) -> None: ...

    @override  # type: ignore[misc]
    def update(  # pyright: ignore[reportIncompatibleMethodOverride,reportInconsistentOverload]
        self,
        other: Mapping[Key, Value]
        | Sequence[tuple[Key, Value]]
        | AbstractSet[tuple[Key, Value]]
        | None = None,
        /,
        **kwargs: Value,
    ) -> None:
        _other: dict[Key, Value] = {}
        if other is not None:
            _other.update(other)
        _other.update(**kwargs)
        self._update_delegate(_other)
