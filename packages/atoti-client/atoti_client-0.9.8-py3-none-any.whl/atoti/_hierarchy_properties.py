from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from pydantic import JsonValue
from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableMapping
from ._identification import CubeIdentifier, HierarchyIdentifier


@final
class HierarchyProperties(DelegatingMutableMapping[str, JsonValue]):
    def __init__(
        self,
        hierarchy_identifier: HierarchyIdentifier,
        /,
        *,
        client: Client,
        cube_identifier: CubeIdentifier,
    ):
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier
        self._hierarchy_identifier: Final = hierarchy_identifier

    @override
    def _get_delegate(self, *, key: str | None) -> Mapping[str, JsonValue]:
        py4j_client = self._client._require_py4j_client()
        return py4j_client.get_hierarchy_properties(
            self._hierarchy_identifier,
            cube_name=self._cube_identifier.cube_name,
            key=key,
        )

    @override
    def _update_delegate(self, other: Mapping[str, JsonValue], /) -> None:
        py4j_client = self._client._require_py4j_client()
        new_value = {**self, **other}
        py4j_client.set_hierarchy_properties(
            self._hierarchy_identifier,
            new_value,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.refresh()

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[str], /) -> None:
        py4j_client = self._client._require_py4j_client()
        new_value = {**self}
        for key in keys or list(new_value):
            del new_value[key]
        py4j_client.set_hierarchy_properties(
            self._hierarchy_identifier,
            new_value,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.refresh()
