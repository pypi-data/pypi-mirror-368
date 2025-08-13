from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from functools import cache
from time import monotonic
from types import UnionType
from typing import (
    Annotated,
    Generic,
    TypeAlias,
    TypeVar,
    Union,
    cast,
    final,
    get_args,  # noqa: TID251
    get_origin,
    overload,
)

from typing_extensions import TypeIs, override

from .._typing import get_type_var_args
from ..mapping_lookup import (
    _CHECK_DEFAULT as _MAPPING_LOOKUP_CHECK_DEFAULT,
    _CONTEXT_VAR as _MAPPING_LOOKUP_CONTEXT_VAR,
    mapping_lookup,
)

KeyBound: TypeAlias = str | tuple[str, ...]
Key = TypeVar("Key", bound=KeyBound)
UnambiguousKey = TypeVar("UnambiguousKey", bound=KeyBound)
Value = TypeVar("Value")


@cache
def _get_key_supported_lengths(key_type: type[KeyBound]) -> frozenset[int]:
    """Return all the number of elements supported by *key_type*.

    Example:
        >>> _get_key_supported_lengths(str)
        frozenset({1})
        >>> _get_key_supported_lengths(Annotated[str, "unused"])
        frozenset({1})
        >>> _get_key_supported_lengths(tuple[str, str])
        frozenset({2})
        >>> _get_key_supported_lengths(str | tuple[str, str])
        frozenset({1, 2})
        >>> _get_key_supported_lengths(
        ...     Annotated[str, "unused"] | tuple[str, str] | tuple[str, str, str]
        ... )
        frozenset({1, 2, 3})
        >>> _get_key_supported_lengths(
        ...     tuple[Annotated[str, "unused"], str]
        ...     | tuple[str, Annotated[str, "unused"], str]
        ... )
        frozenset({2, 3})

    """

    def get_length(argument: object, /) -> int:
        if argument is str or (
            get_origin(argument) is Annotated and get_args(argument)[0] is str
        ):
            return 1

        if get_origin(argument) is tuple:
            return len(get_args(argument))

        raise ValueError(f"Unsupported argument: `{argument}`.")

    return frozenset(
        (get_length(argument) for argument in get_args(key_type))
        if get_origin(key_type) in {Union, UnionType}
        else {get_length(key_type)}
    )


_Default = TypeVar("_Default")
_Key = TypeVar("_Key", bound=KeyBound)


def _get_is_of_key_type(key_type: type[_Key], /) -> Callable[[object], TypeIs[_Key]]:
    def is_of_key_type(value: object, /) -> TypeIs[_Key]:
        supported_lengths = _get_key_supported_lengths(
            key_type  # type: ignore[arg-type]
        )
        match value:
            case str():
                return 1 in supported_lengths
            case () | (_,):  # Empty tuples and single element tuples are never keys.
                return False
            case tuple() if all(isinstance(part, str) for part in value):
                return len(value) in supported_lengths
            case _:
                return False

    return is_of_key_type


class SupportsUncheckedMappingLookup(
    Generic[Key, UnambiguousKey, Value],
    ABC,
):
    __is_key: Callable[[object], TypeIs[Key]]
    __is_unambiguous_key: Callable[[object], TypeIs[UnambiguousKey]]
    __unambiguous_key_length: int

    @override
    def __init_subclass__(cls, *args: object, **kwargs: object) -> None:
        super().__init_subclass__(*args, **kwargs)

        type_var_args = get_type_var_args(cls)
        key_type = cast(
            type[Key],
            type_var_args[Key],  # type: ignore[misc]
        )
        cls.__is_key = _get_is_of_key_type(key_type)
        unambiguous_key_type = cast(
            type[UnambiguousKey],
            type_var_args[UnambiguousKey],  # type: ignore[misc]
        )
        cls.__is_unambiguous_key = _get_is_of_key_type(unambiguous_key_type)
        unambiguous_key_length, *_ = _get_key_supported_lengths(
            unambiguous_key_type  # type: ignore[arg-type]
        )
        assert unambiguous_key_length >= 1
        cls.__unambiguous_key_length = unambiguous_key_length

    @abstractmethod
    def _create_lens(self, key: UnambiguousKey, /) -> Value:
        """Create a value acting as a lens for the given key."""

    @abstractmethod
    def _get_unambiguous_keys(self, *, key: Key | None) -> Sequence[UnambiguousKey]:
        """Return all the unambiguous keys corresponding to the passed *key*."""

    @overload
    def get(self, key: Key, /) -> Value | None: ...

    @overload
    def get(self, key: Key, /, default: _Default) -> _Default | Value: ...

    @final
    def get(
        self, key: Key, /, default: _Default | None = None
    ) -> _Default | Value | None:
        with mapping_lookup(
            # Force checked mode to make the `get` method always available.
            check=True
        ):
            assert isinstance(self, Mapping)
            try:
                return self[key]  # type: ignore[no-any-return]
            except KeyError:
                return default

    @final
    def __contains__(self, key: object, /) -> bool:
        if not self.__class__.__is_key(key):
            # If the passed value does not have the type of a key, it cannot be in the mapping.
            return False

        with mapping_lookup(
            # Force checked mode to make the `in` operator always available.
            check=True
        ):
            try:
                assert isinstance(self, Mapping)
                self[key]
            except KeyError:
                return False
            else:
                return True

    @final
    def _get_delegate(
        self,
        *,
        key: Key | None,
    ) -> Mapping[UnambiguousKey, Value]:
        mapping_lookup_context = _MAPPING_LOOKUP_CONTEXT_VAR.get()
        if key is None or (
            _MAPPING_LOOKUP_CHECK_DEFAULT
            if mapping_lookup_context is None
            else mapping_lookup_context.check
        ):
            start: float = 0 if key is None else monotonic()
            unambiguous_keys = self._get_unambiguous_keys(key=key)
            if key is not None and (
                # Do not waste time updating the report if this call is not inside a `mapping_lookup()` context.
                mapping_lookup_context is not None
            ):
                duration = monotonic() - start
                mapping_lookup_context.report.counts[self.__class__] += 1
                mapping_lookup_context.report.durations[self.__class__] += duration
            return {
                unambiguous_key: self._create_lens(unambiguous_key)
                for unambiguous_key in unambiguous_keys
            }

        if self.__class__.__is_unambiguous_key(key):
            return {key: self._create_lens(key)}

        expected_type = (
            "str"
            if self.__unambiguous_key_length == 1
            else f"({', '.join(['str'] * self.__unambiguous_key_length)})"
        )
        raise ValueError(
            f"Cannot use ambiguous key `{key}` when mapping lookup is unchecked. Pass a `{expected_type}` instead."
        )
