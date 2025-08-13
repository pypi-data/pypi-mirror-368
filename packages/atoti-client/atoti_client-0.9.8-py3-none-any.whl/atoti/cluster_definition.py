from collections.abc import Set as AbstractSet
from typing import final

from pydantic.dataclasses import dataclass

from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .distribution_protocols import DiscoveryProtocol


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ClusterDefinition:
    application_names: AbstractSet[str]
    """The names of the applications allowed to join the cluster."""

    authentication_token: str
    """The token securing the cluster by preventing unwanted nodes from joining.

    All the expected nodes of this cluster must use the same token.
    """

    # Merge this with `cube_url` before making it public.
    # Also move it out of the cluster definition since it does not actually define the cluster.
    cube_port: int | None = None
    """The port from which the cube can be accessed.

    :meta private:
    """

    cube_url: str | None = None
    """The URL from which the cube can be accessed.

    :meta private:
    """

    discovery_protocol: DiscoveryProtocol | None = None
