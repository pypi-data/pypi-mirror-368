from ._check_allowed import check_allowed as _check_allowed


def check_allowed(key: str, /) -> None:
    """Check that a previously :meth:`registered <atoti._experimental.features.Features.register>` feature is allowed.

    See Also:
        :func:`atoti._experimental.experimental`.
    """
    _check_allowed(key)
