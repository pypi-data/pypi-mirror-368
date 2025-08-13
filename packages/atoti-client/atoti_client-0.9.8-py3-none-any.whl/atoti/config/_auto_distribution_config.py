from typing import final

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class AutoDistributionConfig:
    """The config to automatically join a distributed cluster.

    Note:
        This feature is not part of the community edition: it needs to be :doc:`unlocked </guides/unlocking_all_features>`.
    """

    default_application_name: bool = True
    """
    Configures the session to automatically sets an application name for created cubes.

    Without an application name, a cube will be join any cluster by default, nor can be added to cluster.
    With this flag enabled, the cube name will be used as the application name.
    """
    data_cube_url: str | None = None
