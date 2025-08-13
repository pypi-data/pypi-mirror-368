from collections.abc import Callable, Generator, Set as AbstractSet
from contextlib import contextmanager
from warnings import warn

from ._deprecated_warning_category import DEPRECATED_WARNING_CATEGORY
from ._experimental import CONTEXT_VAR as _CONTEXT_VAR, FEATURES as _FEATURES


@contextmanager
def experimental(
    feature_keys: AbstractSet[str] | Callable[[set[str]], AbstractSet[str]], /
) -> Generator[None, None, None]:
    """Create a context allowing to use the experimental features with the passed keys.

    Warning:
        Experimental features are subject to breaking changes in any release.

    Args:
        feature_keys: The keys of the experimental features allowed to be used inside the context.

            If a :class:`~collections.abc.Callable` is passed, it will be called with the keys of all the experimental features and it must return the keys to allow.

    Example:

        .. doctest::
            :hide:

            >>> from ._experimental import experimental
            >>> @experimental("foo")
            ... def foo(): ...
            >>> class Bar:
            ...     @property
            ...     @experimental()
            ...     def prop(self): ...

            >>> @experimental("baz", stability="stable")
            ... def baz(): ...

        By default, calling an experimental function/method raises an error:

        >>> foo()
        Traceback (most recent call last):
            ...
        RuntimeError: This API is experimental, use `with tt.experimental({'foo'}): ...` to allow it.

        >>> bar = Bar()
        >>> bar.prop
        Traceback (most recent call last):
            ...
        RuntimeError: This API is experimental, use `with tt.experimental({'Bar.prop'}): ...` to allow it.

        An experimental feature can be used by passing its key to this function:

        >>> with tt.experimental({"foo"}):
        ...     foo()

        Multiple keys can be passed:

        >>> with tt.experimental({"foo", "Bar.prop"}):
        ...     foo()
        ...     bar.prop

        Nesting is supported too:

        >>> with tt.experimental({"foo"}):
        ...     foo()
        ...     with tt.experimental({"Bar.prop"}):
        ...         foo()
        ...         bar.prop
        ...     foo()

        Once a feature is stabilized, passing its key to this function will raise a deprecation warning:

        >>> with tt.experimental({"baz"}):
        ...     None
        Traceback (most recent call last):
            ...
        FutureWarning: Experimental feature with key `baz` has been stabilized, stop passing its key.

        Passing a key that does not match any feature will raise an error:

        >>> with tt.experimental({"quux"}):  # doctest: +ELLIPSIS
        ...     None
        Traceback (most recent call last):
            ...
        ValueError: No experimental feature with key `quux`, existing keys are ...

        .. doctest::
            :hide:

            >>> for key in ["foo", "Bar.prop", "baz"]:
            ...     _FEATURES.unregister(key)

    """
    if isinstance(feature_keys, Callable):  # type: ignore[arg-type]
        feature_keys = feature_keys(set(_FEATURES.unstable_feature_keys))  # type: ignore[operator]

    previously_allowed_keys = _CONTEXT_VAR.get()

    newly_allowed_keys: set[str] = set()
    for key in feature_keys - previously_allowed_keys:  # type: ignore[operator]
        stability = _FEATURES.stability(key)
        match stability:
            case "experimental":
                newly_allowed_keys.add(key)
            case "stable":
                warn(
                    f"Experimental feature with key `{key}` has been stabilized, stop passing its key.",
                    category=DEPRECATED_WARNING_CATEGORY,
                    stacklevel=3,
                )

    allowed_keys = {*previously_allowed_keys, *newly_allowed_keys}
    token = _CONTEXT_VAR.set(allowed_keys)
    try:
        yield
    finally:
        _CONTEXT_VAR.reset(token)
