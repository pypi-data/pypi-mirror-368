from collections.abc import Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableSet
from ._graphql_client import UpdateDatabaseInput, UpdateDataModelInput
from ._identification import Role


@final
class TablesOwners(DelegatingMutableSet[Role]):
    def __init__(self, *, client: Client) -> None:
        self._client: Final = client

    @override
    def _get_delegate(self) -> AbstractSet[Role]:
        output = self._client._require_graphql_client().get_database_owners()
        return frozenset(output.data_model.database.owners)

    @override
    def _set_delegate(self, new_set: AbstractSet[Role], /) -> None:
        graphql_input = UpdateDataModelInput(
            database=UpdateDatabaseInput(owners=list(new_set))
        )
        self._client._require_graphql_client().update_data_model(input=graphql_input)
