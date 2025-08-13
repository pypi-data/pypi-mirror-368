from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence, Set as AbstractSet
from typing import Generic, TypeVar, final, overload

from typing_extensions import Self, override

from .._ipython import KeyCompletable
from .._typing import get_type_var_args
from .delegating_key_disambiguating_mapping import DelegatingKeyDisambiguatingMapping
from .supports_unchecked_mapping_lookup import (
    Key,
    UnambiguousKey,
    Value as ReadValue,
)

WriteValue = TypeVar("WriteValue")


class _DelegatingConvertingMapping(
    Generic[Key, UnambiguousKey, ReadValue, WriteValue],
    DelegatingKeyDisambiguatingMapping[Key, UnambiguousKey, ReadValue],
    KeyCompletable,
    ABC,
):
    """A `Mapping` that also implements `MutableMapping` methods but where they read and write types can differ."""

    @abstractmethod
    def _update_delegate(
        self,
        other: Mapping[Key, WriteValue],
        /,
    ) -> None: ...

    @overload
    def update(
        self,
        other: Mapping[Key, WriteValue],
        /,
        **kwargs: WriteValue,
    ) -> None: ...

    @overload
    def update(
        self,
        # Using `Sequence | AbstractSet` instead of `Iterable` or `Collection` to have Pydantic validate `other` without converting it to a `ValidatorIterator`.
        other: Sequence[tuple[Key, WriteValue]] | AbstractSet[tuple[Key, WriteValue]],
        /,
        **kwargs: WriteValue,
    ) -> None: ...

    @overload
    def update(self, **kwargs: WriteValue) -> None: ...

    # `MutableMapping` method.
    @final  # type: ignore[misc]
    def update(  # pyright: ignore[reportInconsistentOverload]
        self,
        other: Mapping[Key, WriteValue]
        | Sequence[tuple[Key, WriteValue]]
        | AbstractSet[tuple[Key, WriteValue]]
        | None = None,
        /,
        **kwargs: WriteValue,
    ) -> None:
        _other: dict[Key, WriteValue] = {}
        if other is not None:
            _other.update(other)
        _other.update(**kwargs)
        self._update_delegate(_other)

    # Not a `MutableMapping` method but present on `dict`.
    @final
    def __ior__(self, other: Mapping[Key, WriteValue], /) -> Self:
        self._update_delegate(other)
        return self

    # `MutableMapping` method.
    @final
    def __setitem__(self, key: Key, value: WriteValue, /) -> None:
        self._update_delegate({key: value})

    @abstractmethod
    def _delete_delegate_keys(
        self,
        keys: AbstractSet[Key | UnambiguousKey],
        /,
    ) -> None: ...

    # `MutableMapping` method.
    @final
    def clear(self) -> None:
        return self._delete_delegate_keys(self.keys())

    # `MutableMapping` method.
    @final
    def __delitem__(self, key: Key, /) -> None:
        return self._delete_delegate_keys({key})


class DelegatingConvertingMapping(
    _DelegatingConvertingMapping[Key, UnambiguousKey, ReadValue, WriteValue],
    ABC,
):
    @override
    def __init_subclass__(cls, *args: object, **kwargs: object) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not __debug__:
            return

        type_var_args = get_type_var_args(cls)
        assert type_var_args[ReadValue] is not type_var_args[WriteValue], (  # type: ignore[misc]
            f"`{cls.__name__}` is non-converting (`{ReadValue}` and `{WriteValue}` are both equal to `{type_var_args[ReadValue]}`) and should thus inherit from `{_DelegatingConvertingMapping.__name__}` since the `{cls.set.__name__}` method inherited from `{DelegatingConvertingMapping.__name__}` is useless if the returned value is the same as *value*."  # type: ignore[misc]
        )

    @final
    def set(
        self,
        key: Key,
        value: WriteValue,
        /,
    ) -> ReadValue:
        """Set *key* to *value* and return the converted value.

        Useful to save one line of code:

        .. code-block:: diff

          - mapping[key] = write_value
          - read_value = mapping[key]
          + read_value = mapping.set(key, write_value)
            assert read_value != write_value
            read_value.foo = ...
            read_value.bar(...)

        """
        self[key] = value
        return self[key]
