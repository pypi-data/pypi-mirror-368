"""Existing app extensions to :ref:`customize the app <guides/customizing_the_app:App extensions>`."""

from collections.abc import Mapping as _Mapping
from pathlib import Path as _Path

from ._resources_directory import RESOURCES_DIRECTORY as _RESOURCES_DIRECTORY

_APP_EXTENSIONS_DIRECTORY = _RESOURCES_DIRECTORY / "app-extensions"

_ADVANCED_APP_EXTENSION_NAME = "@activeviam/advanced-extension"

ADVANCED_APP_EXTENSION: _Mapping[str, _Path] = {
    _ADVANCED_APP_EXTENSION_NAME: _APP_EXTENSIONS_DIRECTORY.joinpath(
        *_ADVANCED_APP_EXTENSION_NAME.split("/"),
    ),
}
"""The ``{name: path}`` of an app extension providing the following features:

* MDX editor
* Context values editor
* State editor
* Text editor widget

:meta hide-value:
"""
