from __future__ import annotations

from collections.abc import Callable
from textwrap import dedent
from typing import Any, TypeVar, cast

from ._experimental import get_feature_key_attribute

_T = TypeVar("_T", bound=Callable[..., Any])


# Taken from Pandas:
# https://github.com/pandas-dev/pandas/blame/8aa707298428801199280b2b994632080591700a/pandas/util/_decorators.py#L332
def doc(
    *args: str | Callable[..., Any],
    **kwargs: str,
) -> Callable[[_T], _T]:
    """Take docstring templates, concatenate them and perform string substitution."""

    def decorator(function: _T) -> _T:
        docstring_components: list[str | Callable[..., Any]] = []

        if function.__doc__:
            docstring_components.append(dedent(function.__doc__))

        docstring_components.extend(
            arg for arg in cast(Any, args) if isinstance(arg, str) or arg.__doc__
        )

        if experimental_feature_key := get_feature_key_attribute(function):
            kwargs["experimental_feature"] = (
                f"""This feature is :func:`experimental <atoti.experimental>`, its key is ``"{experimental_feature_key}"``."""
            )

        # Formatting templates and concatenating docstring
        function.__doc__ = "".join(
            [
                arg.format(**kwargs)
                if isinstance(arg, str)
                else dedent(arg.__doc__ or "")
                for arg in docstring_components
            ],
        )

        return function

    return decorator
