from collections.abc import Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableSet
from ._graphql_client import UpdateHierarchyInput
from ._identification import HierarchyIdentifier, Role


@final
class HierarchyViewers(DelegatingMutableSet[Role]):
    def __init__(
        self,
        *,
        cube_name: str,
        hierarchy_identifier: HierarchyIdentifier,
        client: Client,
    ) -> None:
        self._client: Final = client
        self._cube_name: Final = cube_name
        self._hierarchyIdentifier: Final = hierarchy_identifier

    @override
    def _get_delegate(
        self,
    ) -> AbstractSet[Role]:
        output = self._client._require_graphql_client().get_hierarchy_viewers(
            cube_name=self._cube_name,
            dimension_name=self._hierarchyIdentifier.dimension_identifier.dimension_name,
            hierarchy_name=self._hierarchyIdentifier.hierarchy_name,
        )
        return frozenset(output.data_model.cube.dimension.hierarchy.viewers)

    @override
    def _set_delegate(self, new_set: AbstractSet[Role], /) -> None:
        graphql_input = UpdateHierarchyInput(
            cube_name=self._cube_name,
            hierarchy_identifier=self._hierarchyIdentifier._graphql_input,
            viewers=list(new_set),
        )
        self._client._require_graphql_client().update_hierarchy(input=graphql_input)
