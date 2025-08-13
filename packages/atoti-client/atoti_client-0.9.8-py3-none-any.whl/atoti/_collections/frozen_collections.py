"""These frozen collections are documented and seen as type checkers as abstract immutable collections to let users pass any compatible instance.

However, at runtime, they are converted to concrete immutable collections by Pydantic.
It ensures that frozen dataclasses using attributes of these types will be hashable and thus usable as keys in a mapping.
"""

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Annotated, TypeVar

from pydantic import AfterValidator

from .._env import (
    GENERATING_API_REFERENCE_ENV_VAR_NAME as _GENERATING_API_REFERENCE_ENV_VAR_NAME,
    get_env_flag,
)
from .frozendict import Key, Value, _FrozenDict

Element = TypeVar("Element")

FrozenMapping = Annotated[
    Mapping[Key, Value],
    AfterValidator(
        _FrozenDict,  # Using `_FrozenDict` instead of `frozendict` to get back an instance inheriting from `dict` since Pydantic would not know how to serialize the result of `frozendict`.
    ),
]


if TYPE_CHECKING or get_env_flag(_GENERATING_API_REFERENCE_ENV_VAR_NAME):
    FrozenSequence = Sequence[Element]
else:
    # `FrozenSequence` must be re-declared to be serializable and avoid:
    #
    #   pydantic_core._pydantic_core.PydanticSerializationError: Error serializing to JSON: PydanticSerializationError: Error calling function `<lambda>`: UserWarning: Pydantic serializer warnings:
    #   Expected `list[definition-ref]` but got `tuple` - serialized value may not be as expected
    #
    FrozenSequence = tuple[Element, ...]
