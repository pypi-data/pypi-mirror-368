from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableMapping
from ._ipython import ReprJson, ReprJsonable


@final
class SharedContext(DelegatingMutableMapping[str, str], ReprJsonable):  # type: ignore[misc]
    def __init__(self, *, client: Client, cube_name: str) -> None:
        self._client = client
        self._cube_name: Final = cube_name

    @override
    def _get_delegate(self, *, key: str | None) -> Mapping[str, str]:
        return self._client._require_py4j_client().get_shared_context_values(
            cube_name=self._cube_name,
            key=key,
        )

    @override
    def _update_delegate(self, other: Mapping[str, str], /) -> None:
        py4j_client = self._client._require_py4j_client()
        for key, value in other.items():
            py4j_client.set_shared_context_value(
                key,
                str(value),
                cube_name=self._cube_name,
            )
        py4j_client.refresh()

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[str], /) -> None:
        raise NotImplementedError("Cannot delete context value.")

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            dict(self),
            {"expanded": True, "root": "Context Values"},
        )
