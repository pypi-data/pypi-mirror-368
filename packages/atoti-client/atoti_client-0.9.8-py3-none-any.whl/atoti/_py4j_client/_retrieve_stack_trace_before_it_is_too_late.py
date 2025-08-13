from collections.abc import Callable
from functools import wraps
from typing import Any

from py4j.protocol import Py4JError, Py4JJavaError


def retrieve_stack_trace_before_it_is_too_late(
    function: Callable[[Any], Any],
) -> Callable[[Any], Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except Py4JJavaError as error:
            raise Py4JError(str(error)) from error

    return wrapper
