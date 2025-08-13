from functools import cache
from typing import TYPE_CHECKING, TypeVar

from pydantic import TypeAdapter

_TypeT = TypeVar("_TypeT")


def get_type_adapter(_type: type[_TypeT], /) -> TypeAdapter[_TypeT]:
    """Cache the creation of Pydantic type adapters to avoid `performance issues <https://github.com/pydantic/pydantic/blob/e3b4633ebfee9a05cb56a2d325e051caf0cd7560/docs/concepts/type_adapter.md?plain=1#L83-L86>`__."""
    return TypeAdapter(_type)  # pylint: disable=prefer-cached-type-adapter


if not TYPE_CHECKING:
    # Work around https://github.com/python/typeshed/issues/6347.
    get_type_adapter = cache(get_type_adapter)
