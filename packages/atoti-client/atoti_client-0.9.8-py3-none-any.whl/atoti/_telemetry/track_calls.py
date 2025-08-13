from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from dataclasses import field
from datetime import timedelta
from functools import wraps
from time import perf_counter
from typing import TypeVar, final

from pydantic.dataclasses import dataclass
from typing_extensions import ParamSpec

from .._collection_method_names import COLLECTION_METHOD_NAMES
from .._collections import FrozenMapping
from .._decorate_api import get_function_re_exported_path
from .._pydantic import PYDANTIC_CONFIG
from .event import Event
from .get_non_personal_arguments import get_non_personal_arguments
from .get_non_personal_type_name import get_non_personal_type_name
from .send_event import send_event


@final
@dataclass(config=PYDANTIC_CONFIG, frozen=True, kw_only=True)
class CallEvent(Event):
    """Triggered when a function or method from the public API is called."""

    event_type: str = field(default="call", init=False)
    path: str
    duration: timedelta
    arguments: FrozenMapping[str, str]
    error: str | None


@final
class _CallTracker:
    def __init__(self) -> None:
        self.tracking: bool = False


_P = ParamSpec("_P")
_R = TypeVar("_R")


def create_decorator() -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    call_tracker = _CallTracker()

    def decorator(function: Callable[_P, _R], /) -> Callable[_P, _R]:
        if function.__name__ in COLLECTION_METHOD_NAMES:
            # Collection methods do not have Atoti-specific logic so they are not worth tracking.
            return function

        path = get_function_re_exported_path(function.__module__, function.__qualname__)

        @wraps(function)
        def wrapper(
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> _R:
            if call_tracker.tracking:
                return function(*args, **kwargs)

            call_tracker.tracking = True

            try:
                error_type_name = None
                call_time = perf_counter()

                try:
                    return function(*args, **kwargs)
                except Exception as error:
                    with suppress(  # Do nothing to let the previous error be the one presented to the user.
                        Exception,
                    ):
                        error_type_name = get_non_personal_type_name(error)
                    raise
                finally:
                    arguments: dict[str, str] = {}

                    with suppress(Exception):  # Do nothing to not bother the user.
                        arguments = get_non_personal_arguments(
                            function,
                            *args,
                            **kwargs,
                        )

                    duration = timedelta(seconds=perf_counter() - call_time)
                    call_event = CallEvent(
                        path=path,
                        duration=duration,
                        arguments=arguments,
                        error=error_type_name,
                    )

                    send_event(call_event)
            finally:
                call_tracker.tracking = False

        return wrapper

    return decorator
