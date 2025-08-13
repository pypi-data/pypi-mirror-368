from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSet,
    Sequence,
    Set as AbstractSet,
)
from contextlib import AbstractContextManager
from typing import Annotated, Final, final

import pandas as pd
import pyarrow as pa
from pydantic import Field
from typing_extensions import assert_never, override

from ._arrow_utils import get_data_types_from_arrow
from ._client import Client
from ._collections import DelegatingConvertingMapping, SupportsUncheckedMappingLookup
from ._data_type import DataType, data_type_to_graphql
from ._doc import doc
from ._graphql_client import (
    CreateInMemoryTableColumnInput,
    CreateInMemoryTableInput,
    DeleteTableInput,
    create_delete_status_validator,
)
from ._identification import (
    Identifiable,
    Role,
    TableIdentifier,
    TableName,
    identify,
)
from ._ipython import ReprJson, ReprJsonable
from ._pandas_utils import pandas_to_arrow
from ._session_id import SessionId
from ._table_definition import TableDefinition
from ._tables_owners import TablesOwners
from ._tables_readers import TablesReaders
from ._tables_restriction_condition import TablesRestrictionCondition
from ._tables_restrictions import Restrictions
from ._tables_schema import TablesSchema
from ._transaction import (
    TRANSACTION_DOC_KWARGS as _TRANSACTION_DOC_KWARGS,
    transact_data,
)
from .data_load import DataLoad
from .table import Table, _LoadArgument


def _get_create_in_memory_table_input(
    definition: TableDefinition, /, *, identifier: TableIdentifier
) -> CreateInMemoryTableInput:
    columns = {
        column_name: CreateInMemoryTableColumnInput(
            column_name=column_name,
            data_type=data_type_to_graphql(data_type),
        )
        for column_name, data_type in definition.data_types.items()
    }
    for column_name, default_value in definition.default_values.items():
        columns[column_name].default_value = default_value

    primary_index = (
        list(definition.keys)
        if isinstance(definition.keys, Sequence)
        else [
            column_name
            for column_name in definition.data_types
            if column_name in definition.keys
        ]
    )

    graphql_input = CreateInMemoryTableInput(
        columns=list(columns.values()),
        primary_index=primary_index,
        table_name=identifier.table_name,
    )
    if definition.partitioning is not None:
        graphql_input.partitioning = definition.partitioning

    return graphql_input


@final
class Tables(
    SupportsUncheckedMappingLookup[TableName, TableName, Table],
    DelegatingConvertingMapping[TableName, TableName, Table, TableDefinition],
    ReprJsonable,
):
    r"""Manage the local :class:`~atoti.Table`\ s of a :class:`~atoti.Session`."""

    def __init__(
        self,
        *,
        client: Client,
        session_id: SessionId,
    ):
        self._client: Final = client
        self._session_id: Final = session_id

    @override
    def _create_lens(self, key: TableName, /) -> Table:
        return Table(
            TableIdentifier(key),
            client=self._client,
            scenario=None,
        )

    @override
    def _get_unambiguous_keys(self, *, key: TableName | None) -> list[TableName]:
        if key is None:
            output = self._client._require_graphql_client().get_tables()
            return [table.name for table in output.data_model.database.tables]

        output = self._client._require_graphql_client().find_table(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
            table_name=key,
        )
        table = output.data_model.database.table  # type: ignore[attr-defined]
        return [] if table is None else [table.name]

    @override
    def _update_delegate(
        self,
        other: Mapping[TableName, TableDefinition],
        /,
    ) -> None:
        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for table_name, definition in other.items():
                graphql_input = _get_create_in_memory_table_input(
                    definition, identifier=TableIdentifier(table_name)
                )
                graphql_client.create_in_memory_table(input=graphql_input)

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[TableName], /) -> None:
        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for key in keys:
                graphql_input = DeleteTableInput(table_name=key)
                graphql_client.delete_table(input=graphql_input).set_output_validator(
                    create_delete_status_validator(
                        key, lambda output: output.delete_table.status
                    )
                )

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            dict(
                sorted(
                    {
                        table.name: table._repr_json_()[0] for table in self.values()
                    }.items(),
                ),
            ),
            {"expanded": False, "root": "Tables"},
        )

    @doc(
        **_TRANSACTION_DOC_KWARGS,
        countries_table_data_types_argument=r"""{"City": "String", "Country": "String"}""",
        keys_argument=r"""{"City"}""",
        customers_table_data_types_argument=r"""{"Name": "String", "Stock price": "double"}""",
        customers_table_keys_argument=r"""{"Name"}""",
        cities_table=r"{cities_table}",
        customers_table=r"{customers_table}",
        cities_and_customers_tables=r"{cities_table, customers_table}",
        nested_transactions_with_tables_error_message=r"""Cannot start a transaction locking tables {t['Customers']} inside another transaction locking tables {t['Cities']} which is not a superset.""",
        nested_transactions_all_tables_error_message=r"""Cannot start a transaction locking all tables inside another transaction locking a subset of tables: {t['Cities']}.""",
    )
    def data_transaction(
        self,
        scenario_name: str | None = None,
        *,
        allow_nested: bool = True,
        tables: Annotated[
            AbstractSet[Identifiable[TableIdentifier]], Field(min_length=1)
        ]
        | None = None,
    ) -> AbstractContextManager[None]:
        """Create a data transaction to batch several data loading operations.

        * It is more efficient than doing each :meth:`~atoti.Table.load` one after the other, especially when using :meth:`~atoti.Table.load_async` to load data concurrently in multiple tables.
        * It avoids possibly incorrect intermediate states (e.g. if loading some new data requires dropping existing rows first).
        * If an exception is raised during a data transaction, it will be rolled back and the changes made until the exception will be discarded.

        Note:
            Data transactions cannot be mixed with:

            * Long-running data operations such as :meth:`~atoti.Table.stream`.
            * Data model operations such as :meth:`~atoti.Session.create_table`, :meth:`~atoti.Table.join`, or defining a new measure.
            * Operations on parameter tables created from :meth:`~atoti.Cube.create_parameter_hierarchy_from_members` and :meth:`~atoti.Cube.create_parameter_simulation`.
            * Operations on other source scenarios than the one the transaction is started on.

        Args:
            {allow_nested}
            scenario_name: The name of the source scenario impacted by all the table operations inside the transaction.
            tables: The tables that can be affected by this transaction.
                Tables transitively joined with these tables will be locked too.
                Transactions locking disjoint sets of tables execute concurrently.
                When ``None``, all tables are locked.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> cities_df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("Berlin", 150.0),
            ...         ("London", 240.0),
            ...         ("New York", 270.0),
            ...         ("Paris", 200.0),
            ...     ],
            ... )
            >>> cities_table = session.read_pandas(
            ...     cities_df,
            ...     keys={keys_argument},
            ...     table_name="Cities",
            ... )
            >>> extra_cities_df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("Singapore", 250.0),
            ...     ],
            ... )
            >>> with session.tables.data_transaction():
            ...     cities_table += ("New York", 100.0)
            ...     cities_table.drop(cities_table["City"] == "Paris")
            ...     cities_table.load(extra_cities_df)
            >>> cities_table.head().sort_index()
                       Price
            City
            Berlin     150.0
            London     240.0
            New York   100.0
            Singapore  250.0

            .. doctest::
                :hide:

                >>> cities_table.drop()

            If an exception is raised during a data transaction, the changes made until the exception will be rolled back.

            >>> cities_table.load(cities_df)
            >>> cities_table.head().sort_index()
                      Price
            City
            Berlin    150.0
            London    240.0
            New York  270.0
            Paris     200.0
            >>> with session.tables.data_transaction():
            ...     cities_table += ("New York", 100.0)
            ...     cities_table.drop(cities_table["City"] == "Paris")
            ...     cities_table.load(extra_cities_df)
            ...     raise Exception("Some error")
            Traceback (most recent call last):
                ...
            Exception: Some error
            >>> cities_table.head().sort_index()
                      Price
            City
            Berlin    150.0
            London    240.0
            New York  270.0
            Paris     200.0

            .. doctest::
                :hide:

                >>> cities_table.drop()

            Loading data concurrently in multiple tables:

            >>> import asyncio
            >>> countries_table = session.create_table(
            ...     "Countries",
            ...     data_types={countries_table_data_types_argument},
            ...     keys={keys_argument},
            ... )
            >>> cities_table.join(countries_table)
            >>> countries_df = pd.DataFrame(
            ...     columns=["City", "Country"],
            ...     data=[
            ...         ("Berlin", "Germany"),
            ...         ("London", "England"),
            ...         ("New York", "USA"),
            ...         ("Paris", "France"),
            ...     ],
            ... )
            >>> async def load_data_in_all_tables(tables):
            ...     with tables.data_transaction():
            ...         await asyncio.gather(
            ...             tables["Cities"].load_async(cities_df),
            ...             tables["Countries"].load_async(countries_df),
            ...         )
            >>> cities_table.drop()
            >>> asyncio.run(load_data_in_all_tables(session.tables))
            >>> cities_table.head().sort_index()
                      Price
            City
            Berlin    150.0
            London    240.0
            New York  270.0
            Paris     200.0
            >>> countries_table.head().sort_index()
                      Country
            City
            Berlin    Germany
            London    England
            New York      USA
            Paris      France

            .. doctest::
                :hide:

                >>> cities_table.drop()

            Nested transactions allowed:

            >>> def composable_function(session):
            ...     table = session.tables["Cities"]
            ...     with session.tables.data_transaction():
            ...         table += ("Paris", 100.0)
            >>> # The function can be called in isolation:
            >>> composable_function(session)
            >>> cities_table.head().sort_index()
                   Price
            City
            Paris  100.0
            >>> with session.tables.data_transaction(
            ...     allow_nested=False  # No-op because this is the outer transaction.
            ... ):
            ...     cities_table.drop()
            ...     cities_table += ("Berlin", 200.0)
            ...     # The function can also be called inside another transaction and will contribute to it:
            ...     composable_function(session)
            ...     cities_table += ("New York", 150.0)
            >>> cities_table.head().sort_index()
                      Price
            City
            Berlin    200.0
            New York  150.0
            Paris     100.0

            Nested transactions not allowed:

            >>> def not_composable_function(session):
            ...     table = session.tables["Cities"]
            ...     with session.tables.data_transaction(allow_nested=False):
            ...         table.drop()
            ...         table += ("Paris", 100.0)
            ...     assert table.row_count == 1
            >>> # The function can be called in isolation:
            >>> not_composable_function(session)
            >>> with session.tables.data_transaction():
            ...     cities_table.drop()
            ...     cities_table += ("Berlin", 200.0)
            ...     # This is a programming error, the function cannot be called inside another transaction:
            ...     not_composable_function(session)
            ...     cities_table += ("New York", 150.0)
            Traceback (most recent call last):
                ...
            RuntimeError: Cannot start this transaction inside another transaction since nesting is not allowed.
            >>> # The last transaction was rolled back:
            >>> cities_table.head().sort_index()
                   Price
            City
            Paris  100.0

            Restricting the transaction to a subset of tables:

            >>> customers_table = session.create_table(
            ...     "Customers",
            ...     data_types={customers_table_data_types_argument},
            ...     keys={customers_table_keys_argument},
            ... )
            >>> dataframe = pd.DataFrame(
            ...     [("Acme Corporation", 120.0)], columns=list(customers_table)
            ... )
            >>> with session.tables.data_transaction(tables={customers_table}):
            ...     customers_table.load(dataframe)
            ...     # cities_table is not locked and could be updated concurrently in another transaction
            >>> customers_table.head()
                              Stock price
            Name
            Acme Corporation        120.0

            Nested transactions must specify a subset of the outer transaction's tables:

            >>> with session.tables.data_transaction():
            ...     with session.tables.data_transaction(tables={cities_table}):
            ...         pass
            ...     with session.tables.data_transaction(tables={customers_table}):
            ...         pass

            >>> with session.tables.data_transaction(
            ...     tables={cities_and_customers_tables}
            ... ):
            ...     with session.tables.data_transaction(tables={cities_table}):
            ...         pass
            ...     with session.tables.data_transaction(tables={customers_table}):
            ...         pass

            >>> with session.tables.data_transaction(tables={cities_table}):
            ...     with session.tables.data_transaction(tables={customers_table}):
            ...         pass
            Traceback (most recent call last):
                ...
            RuntimeError: {nested_transactions_with_tables_error_message}

            >>> with session.tables.data_transaction(tables={cities_table}):
            ...     with session.tables.data_transaction():
            ...         pass
            Traceback (most recent call last):
                ...
            RuntimeError: {nested_transactions_all_tables_error_message}

        See Also:
            :meth:`~atoti.Session.data_model_transaction`.

        """
        py4j_client = self._client._require_py4j_client()

        table_identifiers = (
            None if tables is None else {identify(table) for table in tables}
        )
        return transact_data(
            allow_nested=allow_nested,
            commit=lambda transaction_id: py4j_client.end_data_transaction(
                transaction_id,
                has_succeeded=True,
            ),
            rollback=lambda transaction_id: py4j_client.end_data_transaction(
                transaction_id,
                has_succeeded=False,
            ),
            session_id=self._session_id,
            start=lambda: py4j_client.start_data_transaction(
                initiated_by_user=True,
                scenario_name=scenario_name,
                table_identifiers=table_identifiers,
            ),
            table_identifiers=table_identifiers,
        )

    def infer_data_types(self, data: _LoadArgument, /) -> dict[str, DataType]:  # pyright: ignore[reportUnknownParameterType]
        """Infer data types from the passed *data*.

        Args:
            data: The data from which data types should be inferred.

        Example:
            .. doctest::
                :hide:

                >>> directory = getfixture("tmp_path")
                >>> session = getfixture("default_session")

            >>> from datetime import date
            >>> dataframe = pd.DataFrame(
            ...     {
            ...         "Id": [1, 2, 3],
            ...         "Name": ["Phone", "Watch", "Laptop"],
            ...         "Price": [849.99, 249.99, 1499.99],
            ...         "Date": [
            ...             date(2024, 11, 27),
            ...             date(2024, 11, 26),
            ...             date(2024, 11, 25),
            ...         ],
            ...     }
            ... )
            >>> session.tables.infer_data_types(dataframe)
            {'Id': 'long', 'Name': 'String', 'Price': 'double', 'Date': 'LocalDate'}

        See Also:
            :meth:`~atoti.Table.load`.
        """
        match data:
            case pa.Table():
                return get_data_types_from_arrow(data)
            case pd.DataFrame():
                arrow_table = pandas_to_arrow(data, data_types={})
                return self.infer_data_types(arrow_table)
            case DataLoad():
                return self._client._require_py4j_client().infer_data_types(data)
            case _:
                assert_never(data)

    @property
    def owners(self) -> MutableSet[Role]:
        """The roles allowing to edit the data in tables and the schema of tables.

        Example:
            >>> session_config = tt.SessionConfig(security=tt.SecurityConfig())
            >>> session = tt.Session.start(session_config)
            >>> table = session.create_table(
            ...     "Table", data_types={"ID": "String", "Value": "int"}, keys={"ID"}
            ... )
            >>> table += ("foo", 42)
            >>> session.tables.owners
            {'ROLE_ADMIN'}
            >>> authentication = tt.BasicAuthentication("username", "passwd")
            >>> session.security.individual_roles[authentication.username] = {
            ...     "ROLE_USER"
            ... }
            >>> session.security.basic_authentication.credentials[
            ...     authentication.username
            ... ] = authentication.password
            >>> connected_session = tt.Session.connect(
            ...     session.url, authentication=authentication
            ... )

            The user has none of the :attr:`owners` roles and is thus not allowed to edit the data in tables:

            >>> connected_session.tables[table.name].drop()  # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            RuntimeError: This Live Extension action is not available. ...

            And not allowed to edit the schema of tables:

            >>> del connected_session.tables[table.name]
            Traceback (most recent call last):
                ...
            atoti._graphql_client.exceptions.GraphQLClientHttpError: HTTP status code: 403

            .. doctest::
                :hide:

                >>> del connected_session
                >>> del session

        See Also:
            :attr:`readers` and :attr:`restrictions`.
        """
        return TablesOwners(client=self._client)

    @property
    def readers(self) -> MutableSet[Role]:
        """The roles allowing to read data from tables.

        Example:
            >>> session_config = tt.SessionConfig(security=tt.SecurityConfig())
            >>> session = tt.Session.start(session_config)
            >>> table = session.create_table(
            ...     "Table", data_types={"ID": "String", "Value": "int"}, keys={"ID"}
            ... )
            >>> table += ("foo", 42)
            >>> session.tables.readers
            {'ROLE_USER'}
            >>> authentication = tt.BasicAuthentication("username", "passwd")
            >>> session.security.individual_roles[authentication.username] = {
            ...     "ROLE_USER"
            ... }
            >>> session.security.basic_authentication.credentials[
            ...     authentication.username
            ... ] = authentication.password
            >>> connected_session = tt.Session.connect(
            ...     session.url, authentication=authentication
            ... )

            The user has one of the :attr:`readers` roles and can thus read data from the table:

            >>> connected_session.tables[table.name].query()
                ID  Value
            0  foo     42

            Changing the :attr:`readers` roles to revoke access:

            >>> session.tables.readers.clear()
            >>> try:
            ...     connected_session.tables[table.name].query()
            ... except Exception as error:
            ...     error.response.status_code
            400

            .. doctest::
                :hide:

                >>> del connected_session
                >>> del session

        See Also:
            :attr:`owners` and :attr:`restrictions`.
        """
        return TablesReaders(client=self._client)

    @property
    def restrictions(self) -> MutableMapping[Role, TablesRestrictionCondition]:
        # Keep this docstring in sync with `Cube.restrictions`.
        """Mapping from role to corresponding restriction.

        Restrictions limit the data accessible to users based on their roles.
        Restrictions apply on table columns and are inherited by all hierarchies based on these columns.

        * Restrictions on different columns/hierarchies are intersected.
        * Restrictions on the same column/hierarchy are unioned.

        Example:
            >>> session_config = tt.SessionConfig(security=tt.SecurityConfig())
            >>> session = tt.Session.start(session_config)
            >>> df = pd.DataFrame(
            ...     [
            ...         ("Asia", "Korea", "KRW"),
            ...         ("Asia", "Japan", "JPY"),
            ...         ("Europe", "France", "EUR"),
            ...         ("Europe", "Germany", "EUR"),
            ...         ("Europe", "Norway", "NOK"),
            ...         ("Europe", "Sweden", "SEK"),
            ...     ],
            ...     columns=["Continent", "Country", "Currency"],
            ... )
            >>> table = session.read_pandas(
            ...     df,
            ...     keys={"Continent", "Country", "Currency"},
            ...     table_name="Restrictions example",
            ... )
            >>> cube = session.create_cube(table)
            >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
            >>> cube.hierarchies["Geography"] = [
            ...     table["Continent"],
            ...     table["Country"],
            ... ]
            >>> for level_name in cube.hierarchies["Geography"]:
            ...     del cube.hierarchies[level_name]

            Adding a user to the session:

            >>> password = "abcdef123456"
            >>> session.security.individual_roles["Rose"] = {"ROLE_USER"}
            >>> session.security.basic_authentication.credentials["Rose"] = password
            >>> rose_session = tt.Session.connect(
            ...     session.url,
            ...     authentication=tt.BasicAuthentication("Rose", password),
            ... )
            >>> rose_table = rose_session.tables[table.name]
            >>> rose_cube = rose_session.cubes[cube.name]

            :guilabel:`ROLE_USER` has no restrictions so all the countries and currencies are accessible from the table:

            >>> rose_table.query().set_index(["Continent", "Country"]).sort_index()
                              Currency
            Continent Country
            Asia      Japan        JPY
                      Korea        KRW
            Europe    France       EUR
                      Germany      EUR
                      Norway       NOK
                      Sweden       SEK

            And from the cube:

            >>> rose_cube.query(
            ...     m["contributors.COUNT"], levels=[l["Country"], l["Currency"]]
            ... )
                                       contributors.COUNT
            Continent Country Currency
            Asia      Japan   JPY                       1
                      Korea   KRW                       1
            Europe    France  EUR                       1
                      Germany EUR                       1
                      Norway  NOK                       1
                      Sweden  SEK                       1

            Assigning a role to Rose to limit her access to :guilabel:`France` only:

            >>> session.tables.restrictions["ROLE_FRANCE"] = (
            ...     table["Country"] == "France"
            ... )
            >>> session.security.individual_roles["Rose"] |= {"ROLE_FRANCE"}
            >>> rose_table.query()
              Continent Country Currency
            0    Europe  France      EUR
            >>> rose_cube.query(
            ...     m["contributors.COUNT"], include_totals=True, levels=[l["Country"]]
            ... )
                              contributors.COUNT
            Continent Country
            Total                              1
            Europe                             1
                      France                   1

            Adding Lena with :guilabel:`ROLE_GERMANY` limiting her access to :guilabel:`Germany` only:

            >>> session.tables.restrictions["ROLE_GERMANY"] = (
            ...     table["Country"] == "Germany"
            ... )
            >>> session.security.individual_roles["Lena"] = {
            ...     "ROLE_GERMANY",
            ...     "ROLE_USER",
            ... }
            >>> session.security.basic_authentication.credentials["Lena"] = password
            >>> lena_session = tt.Session.connect(
            ...     session.url,
            ...     authentication=tt.BasicAuthentication("Lena", password),
            ... )
            >>> lena_table = lena_session.tables[table.name]
            >>> lena_cube = lena_session.cubes[cube.name]
            >>> lena_table.query()
              Continent  Country Currency
            0    Europe  Germany      EUR
            >>> lena_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                              contributors.COUNT
            Continent Country
            Europe    Germany                  1

            Assigning :guilabel:`ROLE_GERMANY` to Rose lets her access the union of the restricted countries:

            >>> session.security.individual_roles["Rose"] |= {"ROLE_GERMANY"}
            >>> session.tables.restrictions
            {'ROLE_FRANCE': t['Restrictions example']['Country'] == 'France', 'ROLE_GERMANY': t['Restrictions example']['Country'] == 'Germany'}
            >>> rose_table.query().set_index(["Continent", "Country"]).sort_index()
                              Currency
            Continent Country
            Europe    France       EUR
                      Germany      EUR
            >>> rose_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                              contributors.COUNT
            Continent Country
            Europe    France                   1
                      Germany                  1

            Restrictions can include multiple elements:

            >>> session.tables.restrictions["ROLE_NORDIC"] = table["Country"].isin(
            ...     "Norway", "Sweden"
            ... )
            >>> session.security.individual_roles["Rose"] |= {"ROLE_NORDIC"}
            >>> rose_table.query().set_index(["Continent", "Country"]).sort_index()
                              Currency
            Continent Country
            Europe    France       EUR
                      Germany      EUR
                      Norway       NOK
                      Sweden       SEK
            >>> rose_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                              contributors.COUNT
            Continent Country
            Europe    France                   1
                      Germany                  1
                      Norway                   1
                      Sweden                   1

            Since :guilabel:`Country` and :guilabel:`Continent` are part of the same :guilabel:`Geography` hierarchy, restrictions on these two levels are unioned:

            >>> session.tables.restrictions["ROLE_ASIA"] = table["Continent"] == "Asia"
            >>> session.security.individual_roles["Rose"] |= {"ROLE_ASIA"}
            >>> rose_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                              contributors.COUNT
            Continent Country
            Asia      Japan                    1
                      Korea                    1
            Europe    France                   1
                      Germany                  1
                      Norway                   1
                      Sweden                   1

            :guilabel:`Currency` is part of a different hierarchy so restrictions on it are intersected with the ones from :guilabel:`Geography`:

            >>> session.tables.restrictions["ROLE_EUR"] = table["Currency"] == "EUR"
            >>> session.security.individual_roles["Rose"] |= {"ROLE_EUR"}
            >>> rose_cube.query(
            ...     m["contributors.COUNT"], levels=[l["Country"], l["Currency"]]
            ... )
                                       contributors.COUNT
            Continent Country Currency
            Europe    France  EUR                       1
                      Germany EUR                       1

            Removing the :guilabel:`ROLE_FRANCE` and :guilabel:`ROLE_GERMANY` roles leaves no remaining accessible countries:

            >>> session.security.individual_roles["Rose"] -= {
            ...     "ROLE_FRANCE",
            ...     "ROLE_GERMANY",
            ... }
            >>> rose_table.query()
            Empty DataFrame
            Columns: [Continent, Country, Currency]
            Index: []
            >>> rose_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
            Empty DataFrame
            Columns: [contributors.COUNT]
            Index: []

            .. doctest::
                :hide:

                >>> del session

        See Also:
            :attr:`owners`, :attr:`readers`, and :attr:`atoti.Cube.restrictions`.

        """
        return Restrictions(client=self._client)

    @property
    def schema(self) -> object:
        """Schema of the tables represented as a `Mermaid <https://mermaid.js.org>`__ entity relationship diagram.

        Each table is represented with 3 or 4 columns:

        #. whether the column's :attr:`~atoti.Column.default_value` is ``None`` (denoted with :guilabel:`nullable`) or not
        #. the column :attr:`~atoti.Column.data_type`
        #. (optional) whether the column is part of the table :attr:`~atoti.Table.keys` (denoted with :guilabel:`PK`) or not
        #. the column :attr:`~atoti.Column.name`

        Example:
            .. raw:: html

                <div class="mermaid">
                erDiagram
                  "Table a" {
                      non-null String "foo"
                      nullable int "bar"
                  }
                  "Table b" {
                      non-null int PK "bar"
                      non-null LocalDate "baz"
                  }
                  "Table c" {
                      non-null String PK "foo"
                      non-null double PK "xyz"
                  }
                  "Table d" {
                      non-null String PK "foo d"
                      non-null double PK "xyz d"
                      nullable float "abc d"
                  }
                  "Table a" }o--o| "Table b" : "bar == bar"
                  "Table a" }o..o{ "Table c" : "foo == foo"
                  "Table c" }o--|| "Table d" : "(foo == “foo d”) & (xyz == “xyz d”)"
                </div>

        """
        output = self._client._require_graphql_client().get_database_schema()
        return TablesSchema(output.data_model)
