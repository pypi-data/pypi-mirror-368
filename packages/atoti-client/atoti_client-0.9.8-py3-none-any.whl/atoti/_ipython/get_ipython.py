from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint: disable=nested-import,undeclared-dependency

    # IPython does not correctly re-export it from `core`.
    from IPython import (  # type: ignore[attr-defined]
        InteractiveShell,  # pyright: ignore[reportPrivateImportUsage]
    )

    # pylint: enable=undeclared-dependency, nested-import


def get_ipython() -> InteractiveShell | None:
    try:
        bool(__IPYTHON__)  # type: ignore[name-defined] # pyright: ignore[reportUndefinedVariable]
    except NameError:
        return None

    # pylint: disable=nested-import,undeclared-dependency

    # IPython does not correctly re-export it from `core`.
    from IPython import (  # type: ignore[attr-defined]
        get_ipython as _get_ipython,  # pyright: ignore[reportPrivateImportUsage]
    )

    # pylint: enable=undeclared-dependency, nested-import

    return _get_ipython()  # type: ignore[no-any-return, no-untyped-call]
