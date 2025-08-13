from collections.abc import Callable
from typing import Any

_FEATURE_KEY_ATTRIBUTE_NAME = "_atoti_experimental_feature_key"


def get_feature_key_attribute(
    function: Callable[..., Any],
    /,
) -> str | None:
    key = getattr(function, _FEATURE_KEY_ATTRIBUTE_NAME, None)
    assert isinstance(key, str | None)
    return key


def set_feature_key_attribute(
    function: Callable[..., Any],
    key: str,
    /,
) -> None:
    setattr(function, _FEATURE_KEY_ATTRIBUTE_NAME, key)
