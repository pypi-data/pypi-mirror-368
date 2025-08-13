from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from ..._client import Client
from ..._collections import DelegatingMutableMapping
from .external_aggregate_table import ExternalAggregateTable


@final
class ExternalAggregateTables(DelegatingMutableMapping[str, ExternalAggregateTable]):
    def __init__(self, *, client: Client):
        self._client: Final = client

    @override
    def _get_delegate(self, *, key: str | None) -> Mapping[str, ExternalAggregateTable]:
        return self._client._require_py4j_client().get_external_aggregate_tables(
            key=key
        )

    @override
    def _update_delegate(self, other: Mapping[str, ExternalAggregateTable], /) -> None:
        py4j_client = self._client._require_py4j_client()
        new_mapping = {**self}
        new_mapping.update(other)
        py4j_client.set_external_aggregate_tables(new_mapping)
        py4j_client.refresh()

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[str], /) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.remove_external_aggregate_tables(keys)
        py4j_client.refresh()
