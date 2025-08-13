from collections.abc import Callable, Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from .._client import Client
from .._collections import DelegatingConvertingMapping, SupportsUncheckedMappingLookup
from .._identification import ClusterIdentifier, ClusterName
from .._ipython import ReprJson, ReprJsonable
from ..cluster_definition import ClusterDefinition
from .cluster import Cluster


@final
class Clusters(
    SupportsUncheckedMappingLookup[ClusterName, ClusterName, Cluster],
    DelegatingConvertingMapping[ClusterName, ClusterName, Cluster, ClusterDefinition],
    ReprJsonable,
):
    def __init__(self, *, client: Client, trigger_auto_join: Callable[[], bool]):
        self._client: Final = client
        self._trigger_auto_join: Final = trigger_auto_join

    @override
    def _create_lens(self, key: ClusterName, /) -> Cluster:
        return Cluster(ClusterIdentifier(key), client=self._client)

    @override
    def _get_unambiguous_keys(self, *, key: ClusterName | None) -> list[ClusterName]:
        return [
            identifier.cluster_name
            for identifier in self._client._require_py4j_client().get_clusters()
        ]

    @override
    def _update_delegate(self, other: Mapping[ClusterName, ClusterDefinition]) -> None:
        py4j_client = self._client._require_py4j_client()

        for cluster_name, cluster_config in other.items():
            py4j_client.create_distributed_cluster(
                cluster_name=cluster_name,
                cluster_config=cluster_config,
            )

        py4j_client.refresh()
        if self._trigger_auto_join():
            py4j_client.auto_join_new_distributed_clusters(cluster_names=other.keys())
            py4j_client.refresh()

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[ClusterName], /) -> None:
        py4j_client = self._client._require_py4j_client()

        for key in keys:
            py4j_client.delete_cluster(ClusterIdentifier(key))

        py4j_client.refresh()

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            {name: cluster._repr_json_()[0] for name, cluster in sorted(self.items())},
            {"expanded": False, "root": "Clusters"},
        )
