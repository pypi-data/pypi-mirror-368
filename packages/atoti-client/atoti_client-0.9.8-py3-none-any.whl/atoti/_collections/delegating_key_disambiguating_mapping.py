from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import (
    Collection,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    ValuesView,
)
from inspect import isclass
from typing import Generic, final

from typing_extensions import override

from .._identification import HasIdentifier
from .._ipython import KeyCompletable
from .._typing import get_type_var_args
from ..mapping_lookup import mapping_lookup
from .supports_unchecked_mapping_lookup import (
    Key,
    SupportsUncheckedMappingLookup,
    UnambiguousKey,
    Value,
)


class DelegatingKeyDisambiguatingMapping(
    Generic[Key, UnambiguousKey, Value],
    Mapping[Key, Value],
    KeyCompletable,
    ABC,
):
    @override
    def __init_subclass__(cls, *args: object, **kwargs: object) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not __debug__:
            return

        type_var_args = get_type_var_args(cls)
        value_arg = type_var_args[Value]

        assert (
            issubclass(cls, SupportsUncheckedMappingLookup)
            or not isclass(value_arg)
            or not issubclass(value_arg, HasIdentifier)
        ), (
            f"`{cls.__name__}`'s parametrizes `{Value}` with `{value_arg.__name__}` which inherits from `{HasIdentifier.__name__}`, this mapping should thus also inherit from `{SupportsUncheckedMappingLookup.__name__}`. Do not forget to also list this mapping in the docstring of `{mapping_lookup.__name__}`."  # type: ignore[misc]
        )

    @abstractmethod
    def _get_delegate(
        self,
        *,
        key: Key | None,
    ) -> Mapping[UnambiguousKey, Value]:
        """Retrieve and return the delegate collection.

        Args:
            key: If not ``None``, only that key needs to be retrieved.
                This is an optimization used by the `__getitem__()` method.
                If *key* is not in the delegate collection, an empty mapping must be returned or a `KeyError` must be raised.
        """

    @final
    @override
    def __getitem__(self, key: Key, /) -> Value:
        delegate = self._get_delegate(key=key)

        match len(delegate):
            case 0:
                raise KeyError(key)
            case 1:
                return next(iter(delegate.values()))
            case _:
                raise ValueError(
                    f"Disambiguate `{key}` to narrow it down to one of {list(delegate)}.",
                )

    @final
    @override
    def __iter__(self) -> Iterator[UnambiguousKey]:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        return iter(self._get_delegate(key=None))

    @final
    @override
    def keys(self) -> KeysView[UnambiguousKey]:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        return self._get_delegate(key=None).keys()

    @final
    @override
    def values(self) -> ValuesView[Value]:
        return self._get_delegate(key=None).values()

    @final
    @override
    def items(self) -> ItemsView[UnambiguousKey, Value]:  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        return self._get_delegate(key=None).items()

    @final
    @override
    def __len__(self) -> int:
        return len(self._get_delegate(key=None))

    @override
    def __repr__(self) -> str:
        # Converting to a `dict` so that implementations of `_get_delegate()` returning a `frozendict` still repr as a regular `dict`.
        return repr(dict(self._get_delegate(key=None)))

    @final
    @override
    def _get_key_completions(self) -> Collection[str]:
        return frozenset(key if isinstance(key, str) else key[-1] for key in self)
