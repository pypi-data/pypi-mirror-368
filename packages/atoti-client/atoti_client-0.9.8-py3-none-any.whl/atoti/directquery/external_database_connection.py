from __future__ import annotations

from typing import TYPE_CHECKING, Final, Generic, Literal, final

from .._identification import ExternalTableIdentifier
from ..aggregate_provider import AggregateProvider
from ._external_aggregate_table import ExternalAggregateTable
from ._external_database_connection_config import ExternalDatabaseConnectionConfigT
from ._external_table_update import ExternalTableUpdate
from .external_tables import ExternalTables

if TYPE_CHECKING:
    from .._client import Client  # pylint: disable=nested-import


@final
class ExternalDatabaseConnection(Generic[ExternalDatabaseConnectionConfigT]):
    def __init__(self, *, client: Client, database_key: str) -> None:
        self._client: Final = client
        self._database_key: Final = database_key

    @property
    def tables(self) -> ExternalTables[ExternalDatabaseConnectionConfigT]:
        """Tables of the external database."""
        table_identifiers = self._client._require_py4j_client().get_external_tables(
            self._database_key
        )
        return ExternalTables(
            table_identifiers,
            client=self._client,
            database_key=self._database_key,
        )

    def _derive_aggregate_table(
        self,
        provider: AggregateProvider,
        /,
        table_identifier: ExternalTableIdentifier,
        *,
        cube_name: str,
    ) -> ExternalAggregateTable:
        """Return the definition of an external aggregate table that can be used to feed the passed aggregate provider.

        Args:
            provider: The definition of the provider to convert.
                For best performance, this provider should be added to the cube after adding the returned aggregate table to the session.
            table_identifier: The identifier of the external table that will be used as the aggregate table.
            cube_name: The name of the cube which will contain the provider.
        """
        return self._client._require_py4j_client().derive_external_aggregate_table(
            provider,
            cube_name=cube_name,
            key=self._database_key,
            table_identifier=table_identifier,
        )

    def _generate_sql(
        self,
        aggregate_table: ExternalAggregateTable,
        /,
        *,
        mode: Literal["create", "insert"],
    ) -> str:
        """Generate an SQL query to interact with the passed aggregate table.

        Args:
            aggregate_table: The aggregate table to interact with.
            mode: The type of SQL query to generate.
        """
        queries = (
            self._client._require_py4j_client().generate_external_aggregate_table_sql(
                aggregate_table,
                key=self._database_key,
            )
        )
        if mode == "create":
            return queries.create
        assert mode == "insert"
        return queries.insert

    def _refresh(self, *updates: ExternalTableUpdate) -> None:
        self._client._require_py4j_client().incremental_refresh(*updates)

    def _update_connection_string_and_password(
        self,
        /,
        *,
        connection_string: str,
        password: str,
    ) -> None:
        self._client._require_py4j_client().external_api(
            self._database_key,
        ).updateConnectionStringAndPassword(connection_string, password)
