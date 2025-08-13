from collections.abc import Collection, Iterator, Mapping
from typing import Any, Final, TypeVar, final, overload

from typing_extensions import Never, override

from .._ipython import KeyCompletable

Key = TypeVar("Key")
Value = TypeVar("Value")


# Consider replacing with MappingProxyType once Pydantic supports it.
# See https://github.com/pydantic/pydantic/issues/6868.
@final
class _FrozenDict(dict[Key, Value], KeyCompletable):
    """:class:`dict` raising an error in all methods allowing mutations."""

    @override
    def __hash__(self) -> int:  # type: ignore[override] # pyright: ignore[reportIncompatibleVariableOverride]
        # Two frozen dicts with the same `key: value`  pairs are equal and must thus have the same hash.
        return hash(frozenset(self.items()))

    @override
    def __setitem__(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    @override
    def __delitem__(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    @override
    def setdefault(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    @override
    def pop(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    @override
    def update(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    def _raise_frozen_error(self) -> Never:
        raise TypeError("The dict is frozen.")

    @override
    def _get_key_completions(self) -> Collection[str]:
        return tuple(key for key in self if isinstance(key, str))


@final
class frozendict(Mapping[Key, Value], KeyCompletable):  # noqa: N801
    __slots__ = ("_data",)

    @overload
    def __init__(self, /) -> None: ...

    @overload
    def __init__(self, data: Mapping[Key, Value], /) -> None: ...

    def __init__(self, data: Mapping[Key, Value] | None = None, /) -> None:
        self._data: Final = _FrozenDict() if data is None else _FrozenDict(data)

    @override
    def __getitem__(self, key: Key, /) -> Value:
        return self._data[key]

    @override
    def __hash__(self) -> int:
        return hash(self._data)

    @override
    def __iter__(self) -> Iterator[Key]:
        return iter(self._data)

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict(self)!r})"

    @override
    def _get_key_completions(self) -> Collection[str]:
        return self._data._get_key_completions()
