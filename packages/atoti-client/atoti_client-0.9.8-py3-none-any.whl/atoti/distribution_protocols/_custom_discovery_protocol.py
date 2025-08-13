from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .discovery_protocol import DiscoveryProtocol


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class CustomDiscoveryProtocol(DiscoveryProtocol):
    """Protocol for advanced users, accepting raw XML configuration for JGroups.

    Note:
        While Atoti bundles most discovery protocols offered by JGroups, any required additional dependencies must be provided in :attr:`~atoti.SessionConfig.extra_jars`.

    The following example demonstrates how to use the `CustomDiscoveryProtocol` to configure the `S3_PING` protocol manually.

    Example:
        Configuring :guilabel:`S3_PING` manually:

        >>> protocol = CustomDiscoveryProtocol(
        ...     name="MY_S3_PING",
        ...     # Taken from http://www.jgroups.org/manual/#_s3_ping.
        ...     xml='<MY_S3_PING location="my_bucket" />',
        ... )
        >>> protocol.name
        'MY_S3_PING'
        >>> protocol.xml
        '<MY_S3_PING location="my_bucket" />'

    """

    name: str
    """User-chosen name of the protocol.

    This value is not used by Atoti Server, it only provides a convenient way to identify the protocol.
    """

    xml: str
    """The XML defining the protocol"""

    @property
    @override
    def _name(self) -> str:
        return self.name

    @property
    @override
    def _xml(self) -> str:
        return self.xml
