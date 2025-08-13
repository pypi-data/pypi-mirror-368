from __future__ import annotations

import os
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, TypeAlias, final

from _atoti_core import (
    LICENSE_KEY_ENV_VAR_NAME as _LICENSE_KEY_ENV_VAR_NAME,
    LicenseKeyLocation,
    Plugin,
    get_installed_plugins,
)
from pydantic import DirectoryPath, Field, FilePath, PlainSerializer
from pydantic.dataclasses import dataclass

from .._collections import FrozenMapping, FrozenSequence, frozendict
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._auto_distribution_config import AutoDistributionConfig
from .branding_config import BrandingConfig
from .i18n_config import I18nConfig
from .logging_config import LoggingConfig
from .security_config import SecurityConfig

if TYPE_CHECKING:
    # pylint: disable=nested-import,undeclared-dependency
    from atoti_jdbc import UserContentStorageConfig as _UserContentStorageConfig
else:
    try:
        # pylint: disable=nested-import,undeclared-dependency
        from atoti_jdbc import UserContentStorageConfig as _UserContentStorageConfig
    except ImportError:
        _UserContentStorageConfig: TypeAlias = None  # type: ignore[no-redef] # spell-checker:disable-line


def _get_default_license_key_location() -> LicenseKeyLocation:
    return (
        LicenseKeyLocation.ENVIRONMENT
        if _LICENSE_KEY_ENV_VAR_NAME in os.environ
        else LicenseKeyLocation.EMBEDDED
    )


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class SessionConfig:
    """The config passed to :meth:`atoti.Session.start`."""

    app_extensions: Annotated[
        FrozenMapping[str, DirectoryPath],
        PlainSerializer(
            lambda app_extensions: app_extensions
            or None,  # Remove empty mapping because the community edition does not allow this config option.
        ),
    ] = frozendict()
    """Mapping from the name of an extension (i.e. :guilabel:`name` property in their :guilabel:`package.json`) to the path of its :guilabel:`dist` directory.

    Note:
        This feature is not part of the community edition: it needs to be :doc:`unlocked </guides/unlocking_all_features>`.

    Extensions can :doc:`enhance the app </guides/customizing_the_app>` in many ways such as:

    * Adding new widget plugins.
    * Attaching custom menu items or titlebar buttons to a set of widgets.
    * Providing other React contexts to the components rendered by the app.

    The :download:`app extension template <../app-extension-template.zip>` can be used as a starting point.

    See Also:
        Available extensions in :mod:`atoti.app_extension`.
    """

    # Change this to `distribution: DistributionConfig` with an `auto_join` attribute before making it public.
    auto_distribution: AutoDistributionConfig | None = None
    """:meta private:"""

    branding: BrandingConfig | None = None

    extra_jars: Annotated[FrozenSequence[FilePath], Field(exclude=True)] = ()
    """The paths of the JARs to add to the classpath of the Java subprocess."""

    i18n: I18nConfig | None = None

    java_options: Annotated[FrozenSequence[str], Field(exclude=True)] = ()
    """The additional options to pass when starting the Java subprocess (e.g. for optimization or debugging purposes).

    In particular, the ``-Xmx`` option can be set to increase the amount of RAM that the session can use.

    If this option is not specified, the JVM default memory setting is used which is 25% of the machine memory.
    """

    license_key: Annotated[LicenseKeyLocation | str, Field(exclude=True)] = field(
        default_factory=_get_default_license_key_location
    )
    """The license key required to start the session.

    Defaults to ``Location.ENVIRONMENT`` if the :guilabel:`ATOTI_LICENSE` environment variable is defined, and to ``Location.EMBEDDED`` otherwise.

    :meta private:
    """

    logging: LoggingConfig | None = None

    plugins: Annotated[FrozenMapping[str, Plugin], Field(exclude=True)] = field(
        default_factory=get_installed_plugins
    )
    """The plugins that the session will use.

    :meta private:
    """

    port: Annotated[int, Field(exclude=True)] = 0
    """The port on which the session will listen to.

    If ``0``, the OS will pick an available port.
    """

    ready: bool = True
    """The initial value of :attr:`atoti.Session.ready`."""

    security: Annotated[
        SecurityConfig | None,
        Field(serialization_alias="authentication"),
    ] = None

    user_content_storage: Path | _UserContentStorageConfig | None = None
    """The config controlling how user content is stored.

    If a ``Path`` is given, the content will be stored in the corresponding directory.
    If ``None``, the content will be stored in memory and will be lost when the session is closed.
    """
