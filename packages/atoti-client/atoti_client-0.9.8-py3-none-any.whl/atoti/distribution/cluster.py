from typing import Final, final

from typing_extensions import override

from .._client import Client
from .._identification import (
    ApplicationNames,
    ClusterIdentifier,
    ClusterName,
    HasIdentifier,
)
from .._ipython import ReprJson, ReprJsonable
from ..distribution_protocols import DiscoveryProtocol


@final
class Cluster(HasIdentifier[ClusterIdentifier], ReprJsonable):
    def __init__(self, identifier: ClusterIdentifier, /, *, client: Client):
        self._client: Final = client
        self.__identifier: Final = identifier

    @property
    def name(self) -> ClusterName:
        """The name of the cluster."""
        return self._identifier.cluster_name

    @property
    def application_names(self) -> ApplicationNames:
        """The names of the applications allowed to join the cluster."""
        return frozenset(
            self._client._require_py4j_client().get_cluster_application_names(
                self._identifier
            )
        )

    # This always returns `None` or a `CustomDiscoveryProtocol`.
    # Do not make this public until it instead returns the same class as the one that was passed to `ClusterDefinition`.
    @property
    def _discovery_protocol(self) -> DiscoveryProtocol | None:
        """The discovery protocol used by the cluster."""
        return self._client._require_py4j_client().get_cluster_discovery_protocol(
            self._identifier
        )

    @property
    @override
    def _identifier(self) -> ClusterIdentifier:
        return self.__identifier

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            {
                "name": self.name,
                "application_names": self.application_names,
            },
            {"expanded": False, "root": self.name},
        )
