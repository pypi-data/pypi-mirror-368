from collections.abc import Callable
from typing import TypeVar

from typing_extensions import ParamSpec

_P = ParamSpec("_P")
_R = TypeVar("_R")


def compose_decorators(
    *decorators: Callable[[Callable[_P, _R]], Callable[_P, _R]],
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    def composed_decorator(function: Callable[_P, _R]) -> Callable[_P, _R]:
        for decorator in reversed(decorators):
            function = decorator(function)
        return function

    return composed_decorator
