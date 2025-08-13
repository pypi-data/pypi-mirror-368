from collections.abc import Callable
from typing import Any


def infer_key(function: Callable[..., Any], /) -> str:
    if isinstance(function, property):
        assert function.fget is not None
        return infer_key(function.fget)

    if "." in function.__qualname__:
        return function.__qualname__.removesuffix(".__init__")

    module_name = function.__module__.removeprefix("atoti.").removesuffix(
        f".{function.__name__}"
    )
    return f"{module_name}.{function.__name__}"
