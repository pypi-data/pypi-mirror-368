from collections.abc import Callable
from typing import Any, overload

from .attribute import get_feature_key_attribute
from .context_var import CONTEXT_VAR


@overload
def check_allowed(function: Callable[..., Any], /) -> None: ...


@overload
def check_allowed(key: str, /) -> None: ...


def check_allowed(function_or_key: Callable[..., Any] | str, /) -> None:
    match function_or_key:
        case str() as key:
            allowed_keys = CONTEXT_VAR.get()
            if key not in allowed_keys:
                import atoti as tt  # pylint: disable=nested-import

                argument = {key}
                raise RuntimeError(
                    f"""This API is experimental, use `with tt.{tt.experimental.__name__}({argument}): ...` to allow it."""
                )
        case _ as function:
            _key = get_feature_key_attribute(function)
            assert _key
            check_allowed(_key)
