from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from .._env import GENERATING_API_REFERENCE_ENV_VAR_NAME, get_env_flag
from ._check_allowed import check_allowed
from .attribute import set_feature_key_attribute
from .features import DEFAULT_STABILITY, FEATURES, Stability
from .infer_key import infer_key

_P = ParamSpec("_P")
_R = TypeVar("_R")


def experimental(
    key: str | None = None,
    /,
    *,
    stability: Stability = DEFAULT_STABILITY,
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Create a decorator marking the passed function/method/property as experimental.

    See Also:
        :func:`atoti._experimental.check_allowed`.
    """

    def decorator(function: Callable[_P, _R], /) -> Callable[_P, _R]:
        _key = infer_key(function) if key is None else key
        FEATURES.register(_key, stability=stability)
        result = function

        match stability:
            case "experimental":
                if not get_env_flag(GENERATING_API_REFERENCE_ENV_VAR_NAME):

                    @wraps(function)
                    def wrapper(
                        *args: _P.args,
                        **kwargs: _P.kwargs,
                    ) -> _R:
                        check_allowed(wrapper)
                        return function(*args, **kwargs)

                    result = wrapper

                set_feature_key_attribute(result, _key)
            case "stable":
                ...

        return result

    return decorator
