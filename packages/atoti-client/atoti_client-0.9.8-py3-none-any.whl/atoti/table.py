from __future__ import annotations

import pathlib
import tempfile
from asyncio import to_thread
from collections.abc import Collection, Iterator, Mapping, Sequence
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final, TypeAlias, final

import pandas as pd
import pyarrow as pa
from numpy.typing import NDArray
from pydantic import PositiveInt
from typing_extensions import Self, assert_never, deprecated, override

from ._arrow_utils import write_arrow_to_file
from ._check_column_condition_table import check_column_condition_table
from ._client import Client
from ._collections import frozendict
from ._column_definition import ColumnDefinition
from ._columns import Columns
from ._constant import Constant
from ._default_query_timeout import DEFAULT_QUERY_TIMEOUT as _DEFAULT_QUERY_TIMEOUT
from ._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from ._graphql_client import CreateJoinInput, JoinMappingItemInput
from ._identification import (
    ColumnName,
    HasIdentifier,
    TableIdentifier,
    TableName,
)
from ._ipython import KeyCompletable, ReprJson, ReprJsonable
from ._java import JAVA_INT_RANGE as _JAVA_INT_RANGE
from ._operation import dict_from_condition
from ._pandas_utils import pandas_to_arrow
from ._relationship_optionality import (
    RelationshipOptionality,
    relationship_optionality_to_graphql as relashionship_optionality_to_graphql,
)
from ._report import TableReport
from ._table_drop_filter_condition import TableDropFilterCondition
from ._table_join_mapping_condition import TableJoinMappingCondition
from ._table_query import execute_query
from ._table_query_filter_condition import TableQueryFilterCondition
from ._typing import Duration
from .client_side_encryption_config import (
    ClientSideEncryptionConfig,
)
from .column import Column
from .data_load import CsvLoad, DataLoad, ParquetLoad
from .data_load._arrow_load import ArrowLoad
from .data_stream import DataStream

if TYPE_CHECKING:
    # pyspark is an optional dependency.
    from pyspark.sql import (  # pylint: disable=nested-import,undeclared-dependency
        DataFrame as SparkDataFrame,
    )
else:
    try:
        # pyspark is an optional dependency.
        from pyspark.sql import (  # pylint: disable=nested-import,undeclared-dependency
            DataFrame as SparkDataFrame,
        )
    except ImportError:
        # Custom class to avoid typing `SparkDataFrame` as `object` which would make `_load()` accept any value (i.e. broken runtime type checking).
        @final
        class SparkDataFrame: ...


_LoadArgument: TypeAlias = pa.Table | pd.DataFrame | DataLoad
_Row: TypeAlias = tuple[Constant | None, ...] | Mapping[ColumnName, Constant | None]


@final
# Not inheriting from `Mapping` to avoid confusion with `Mapping.__len__()` that returns the number of columns and `Table.row_count` that returns the number of rows.
# `Mapping`'s `keys()`, `values()`, and `items()` could also be misleading are not thus not implemented.
class Table(HasIdentifier[TableIdentifier], KeyCompletable, ReprJsonable):
    """In-memory table of a :class:`~atoti.Session`.

    .. doctest::
        :hide:

        >>> session = getfixture("default_session")

    >>> table = session.create_table(
    ...     "Example",
    ...     data_types={"Product": "String", "Quantity": "int"},
    ... )

    Listing all the column names:

    >>> list(table)
    ['Product', 'Quantity']

    Testing if the table has a given column:

    >>> "Product" in table
    True
    >>> "Price" in table
    False

    """

    def __init__(
        self,
        identifier: TableIdentifier,
        /,
        *,
        client: Client,
        scenario: str | None,
    ) -> None:
        self._client: Final = client
        self.__identifier: Final = identifier
        self._scenario: Final = scenario

    @property
    def name(self) -> TableName:
        """Name of the table."""
        return self._identifier.table_name

    @property
    @override
    def _identifier(self) -> TableIdentifier:
        return self.__identifier

    @property
    def _columns(self) -> Mapping[ColumnName, Column]:
        return Columns(client=self._client, table_identifier=self._identifier)

    @property
    @deprecated(
        "`Table.columns` is deprecated, use `list(table)` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def columns(self) -> Sequence[ColumnName]:
        """Names of the columns of the table.

        :meta private:
        """
        return list(self)

    @property
    def keys(self) -> Sequence[ColumnName]:
        """Names of the key columns of the table.

        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        When a table does not have keys, adding the same row twice will result in two identical rows in the table:

        >>> table = session.create_table(
        ...     "No keys", data_types={"Product": "String", "Quantity": "int"}
        ... )
        >>> table.keys
        ()
        >>> table += ("Book", 42)
        >>> table += ("Book", 42)
        >>> table.row_count
        2
        >>> table.head().sort_index()
          Product  Quantity
        0    Book        42
        1    Book        42

        The identical rows can be deleted:

        >>> table.drop((table["Product"] == "Book") & (table["Quantity"] == 42))
        >>> table.row_count
        0

        When a table has some keys, inserting a new row with key values equal to the ones of an existing row will overwrite the old row:

        >>> table = session.create_table(
        ...     "Some keys",
        ...     data_types={
        ...         "Country": "String",
        ...         "City": "String",
        ...         "Year": "int",
        ...         "Population": "int",
        ...     },
        ...     keys={"Country", "City"},
        ... )
        >>> table.keys
        ('Country', 'City')
        >>> table += ("France", "Paris", 2000, 9_737_000)
        >>> table += ("United States", "San Diego", 2000, 2_681_000)
        >>> table.head().sort_index()
                                 Year  Population
        Country       City
        France        Paris      2000     9737000
        United States San Diego  2000     2681000
        >>> table += ("France", "Paris", 2024, 11_277_000)
        >>> table.head().sort_index()
                                 Year  Population
        Country       City
        France        Paris      2024    11277000
        United States San Diego  2000     2681000

        """
        output = self._client._require_graphql_client().get_table_primary_index(
            table_name=self.name
        )
        return tuple(
            column.name for column in output.data_model.database.table.primary_index
        )

    @property
    def scenario(self) -> str | None:
        """Scenario on which the table is."""
        return self._scenario

    @property
    def _partitioning(self) -> str:
        """Table partitioning."""
        return self._client._require_py4j_client().get_table_partitioning(
            self._identifier
        )

    def join(
        self,
        target: Table,
        mapping: TableJoinMappingCondition | None = None,
        /,
        *,
        target_optionality: RelationshipOptionality = "optional",
    ) -> None:
        """Define a join between this source table and the *target* table.

        There are two kinds of joins:

        * full join if all the key columns of the *target* table are mapped and the joined tables share the same locality (either both :class:`~atoti.Table` or both ``ExternalTable``).
        * partial join otherwise.

        Depending on the cube creation mode, the join will also generate different hierarchies and measures:

        * ``manual``: No hierarchy is automatically created.
          For partial joins, creating a hierarchy for each mapped key column is necessary before creating hierarchies for the other columns.
          Once these required hierarchies exist, hierarchies for the un-mapped key columns of the *target* table will automatically be created.
        * ``no_measures``: All the key columns and non-numeric columns of the *target* table will be converted into hierarchies.
          No measures will be created in this mode.
        * ``auto``: The same hierarchies as in the ``no_measures`` mode will be created.
          Additionally, columns of the fact table containing numeric values (including arrays), except for columns which are keys, will be converted into measures.
          Columns of the *target* table with these types will not be converted into measures.

        Args:
            target: The other table to join.
            mapping: An equality-based condition from columns of this table to columns of the *target* table.
              If ``None``, the key columns of the *target* table with the same name as columns in this table will be used.
            target_optionality: The relationship optionality on the *target* table side.

              * ``"optional"`` declares no constraints: a row in the source table does not need to have a matching row in the *target* table.
              * ``"mandatory"`` declares that every row in the source table has at least one matching row in the *target* table at all time.
                In the future, this hint will enable some optimizations when incrementally refreshing DirectQuery data.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> sales_table = session.create_table(
            ...     "Sales",
            ...     data_types={"ID": "String", "Product ID": "String", "Price": "int"},
            ... )
            >>> products_table = session.create_table(
            ...     "Products",
            ...     data_types={"ID": "String", "Name": "String", "Category": "String"},
            ... )
            >>> sales_table.join(
            ...     products_table, sales_table["Product ID"] == products_table["ID"]
            ... )

        """
        normalized_mapping: Mapping[str, str] | None = None

        if mapping is not None:
            check_column_condition_table(
                mapping,
                attribute_name="subject",
                expected_table_identifier=self._identifier,
            )
            check_column_condition_table(
                mapping,
                attribute_name="target",
                expected_table_identifier=target._identifier,
            )
            normalized_mapping = {
                source_identifier.column_name: target_identifier.column_name
                for source_identifier, target_identifier in dict_from_condition(
                    mapping,
                ).items()
            }

        graphql_input = CreateJoinInput(
            join_name=target.name,
            source_table_name=self.name,
            target_optionality=relashionship_optionality_to_graphql(target_optionality),
            target_table_name=target.name,
        )
        if normalized_mapping is not None:
            graphql_input.mapping_items = [
                JoinMappingItemInput(
                    source_column_name=source_column_name,
                    target_column_name=target_column_name,
                )
                for source_column_name, target_column_name in normalized_mapping.items()
            ]
        self._client._require_graphql_client().create_join(input=graphql_input)

    @property
    def scenarios(self) -> _TableScenarios:
        """All the scenarios the table can be on."""
        if self.scenario is not None:
            raise RuntimeError(
                "You can only create a new scenario from the base scenario",
            )

        return _TableScenarios(self._identifier, client=self._client)

    @property
    def _loading_report(self) -> TableReport:
        py4j_client = self._client._require_py4j_client()
        return TableReport(
            _clear_reports=py4j_client.clear_loading_report,
            _get_reports=py4j_client.get_loading_report,
            _identifier=self._identifier,
        )

    def __iter__(self) -> Iterator[ColumnName]:
        # Same signature as `Mapping.__iter__()`.
        return iter(self._columns)

    # Implemented for the same reason as `DelegatingKeyDisambiguatingMapping.__contains__()`.
    def __contains__(self, key: object, /) -> bool:
        return key in self._columns

    def __getitem__(self, key: ColumnName, /) -> Column:
        # Same signature as `Mapping.__getitem__()`.
        return self._columns[key]

    @property
    def row_count(self) -> int:
        """The number of rows in the table.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> table = session.create_table(
            ...     "Example",
            ...     data_types={"Product": "String", "Quantity": "int"},
            ... )
            >>> table.row_count
            0
            >>> table += ("Book", 3)
            >>> table.row_count
            1

        """
        return self._client._require_py4j_client().get_table_size(
            self._identifier,
            scenario_name=self.scenario,
        )

    @override
    def _get_key_completions(self) -> Collection[str]:
        return self._columns

    @deprecated(
        "`table.append(rows)` is deprecated, use `table.load(pd.DataFrame(rows, columns=list(table)))` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def append(self, *rows: _Row) -> None:
        """Add one or multiple rows to the table.

        :meta private:
        """
        dataframe = pd.DataFrame(rows, columns=list(self))
        self.load(dataframe)

    def __iadd__(self, row: _Row, /) -> Self:
        dataframe = pd.DataFrame([row], columns=list(self)[: len(row)])
        self.load(dataframe)
        return self

    def drop(
        self,
        filter: TableDropFilterCondition | None = None,  # noqa: A002
        /,
    ) -> None:
        """Delete some of the table's rows.

        Args:
            filter: Rows where this condition evaluates to ``True`` will be deleted.
                If ``None``, all the rows will be deleted.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("London", 240.0),
            ...         ("New York", 270.0),
            ...         ("Paris", 200.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, keys={"City"}, table_name="Cities")
            >>> table.head().sort_index()
                      Price
            City
            London    240.0
            New York  270.0
            Paris     200.0
            >>> table.drop((table["City"] == "Paris") | (table["Price"] <= 250.0))
            >>> table.head().sort_index()
                      Price
            City
            New York  270.0
            >>> table.drop()
            >>> table.row_count
            0
        """
        if filter is not None:
            check_column_condition_table(
                filter,
                attribute_name="subject",
                expected_table_identifier=self._identifier,
            )
        self._client._require_py4j_client().delete_rows_from_table(
            self._identifier,
            scenario_name=self.scenario,
            condition=filter,
        )

    @override
    def _repr_json_(self) -> ReprJson:
        return {
            name: column._repr_json_()[0] for name, column in self._columns.items()
        }, {"expanded": True, "root": self.name}

    def head(self, n: PositiveInt = 5) -> pd.DataFrame:
        """Return at most *n* random rows of the table.

        If the table has some :attr:`keys`, the returned DataFrame will be indexed by them.
        """
        result = self.query(max_rows=n)

        if self.keys:
            result = result.set_index(list(self.keys))

        return result

    def load(
        self,
        data: _LoadArgument,  # pyright: ignore[reportUnknownParameterType]
        /,
    ) -> None:
        """Load data into the table.

        This is a blocking operation: the method will not return until all the data is loaded.

        Args:
            data: The data to load.

        Example:
            .. doctest::
                :hide:

                >>> from jdk4py import JAVA_HOME
                >>> # Use JVM embedded in jdk4py so that running the test does not require a separate JVM installation.
                >>> monkeypatch = getfixture("monkeypatch")
                >>> monkeypatch.setenv("JAVA_HOME", str(JAVA_HOME))
                >>> session = getfixture("default_session")

            >>> from datetime import date
            >>> table = session.create_table(
            ...     "Sales",
            ...     data_types={
            ...         "ID": "String",
            ...         "Product": "String",
            ...         "Price": "int",
            ...         "Quantity": "int",
            ...         "Date": "LocalDate",
            ...     },
            ...     keys={"ID"},
            ... )

            Loading an Arrow table:

            >>> import pyarrow as pa
            >>> arrow_table = pa.Table.from_pydict(
            ...     {
            ...         "ID": pa.array(["ab", "cd"]),
            ...         "Product": pa.array(["phone", "watch"]),
            ...         "Price": pa.array([699, 349]),
            ...         "Quantity": pa.array([1, 2]),
            ...         "Date": pa.array([date(2024, 3, 5), date(2024, 12, 12)]),
            ...     }
            ... )
            >>> table.load(arrow_table)
            >>> table.head().sort_index()
               Product  Price  Quantity       Date
            ID
            ab   phone    699         1 2024-03-05
            cd   watch    349         2 2024-12-12

            Loading a pandas DataFrame:

            >>> import pandas as pd
            >>> pandas_dataframe = pd.DataFrame(
            ...     {
            ...         "ID": ["ef", "gh"],
            ...         "Product": ["laptop", "book"],
            ...         "Price": [2599, 19],
            ...         "Quantity": [3, 5],
            ...         "Date": [date(2023, 8, 10), date(2024, 1, 13)],
            ...     }
            ... )
            >>> table.load(pandas_dataframe)
            >>> table.head().sort_index()
               Product  Price  Quantity       Date
            ID
            ab   phone    699         1 2024-03-05
            cd   watch    349         2 2024-12-12
            ef  laptop   2599         3 2023-08-10
            gh    book     19         5 2024-01-13

            Loading a NumPy array by converting it to a pandas DataFrame:

            >>> import numpy as np
            >>> numpy_array = np.asarray(
            ...     [
            ...         ["ij", "watch", 299, 1, date(2022, 7, 20)],
            ...         ["kl", "keyboard", 69, 1, date(2023, 5, 8)],
            ...     ],
            ...     dtype=object,
            ... )
            >>> table.load(pd.DataFrame(numpy_array, columns=list(table)))
            >>> table.head(10).sort_index()
                 Product  Price  Quantity       Date
            ID
            ab     phone    699         1 2024-03-05
            cd     watch    349         2 2024-12-12
            ef    laptop   2599         3 2023-08-10
            gh      book     19         5 2024-01-13
            ij     watch    299         1 2022-07-20
            kl  keyboard     69         1 2023-05-08

            Loading a Spark DataFrame by converting it to a pandas DataFrame:

            .. doctest::
                :hide:

                >>> # Remove this warning catcher once pyspark 4 is released.
                >>> import pytest
                >>> pytest_warns_context = pytest.warns()
                >>> _ = pytest_warns_context.__enter__()

            >>> from pyspark.sql import Row, SparkSession
            >>> spark = SparkSession.builder.getOrCreate()
            >>> spark_dataframe = spark.createDataFrame(
            ...     [
            ...         Row(
            ...             ID="mn",
            ...             Product="glasses",
            ...             Price=129,
            ...             Quantity=2,
            ...             Date=date(2021, 3, 3),
            ...         ),
            ...         Row(
            ...             ID="op",
            ...             Product="battery",
            ...             Price=49,
            ...             Quantity=2,
            ...             Date=date(2024, 11, 7),
            ...         ),
            ...     ]
            ... )
            >>> table.load(spark_dataframe.toPandas())
            >>> spark.stop()
            >>> table.head(10).sort_index()
                 Product  Price  Quantity       Date
            ID
            ab     phone    699         1 2024-03-05
            cd     watch    349         2 2024-12-12
            ef    laptop   2599         3 2023-08-10
            gh      book     19         5 2024-01-13
            ij     watch    299         1 2022-07-20
            kl  keyboard     69         1 2023-05-08
            mn   glasses    129         2 2021-03-03
            op   battery     49         2 2024-11-07

            .. doctest::
                :hide:

                >>> pytest_warns_context.__exit__(None, None, None)

            The :guilabel:`+=` operator is available as syntax sugar to load a single row expressed either as a :class:`tuple` or a :class:`~collections.abc.Mapping`:

            >>> table += ("qr", "mouse", 29, 3, date(2024, 11, 7))
            >>> table.head(10).sort_index()
                 Product  Price  Quantity       Date
            ID
            ab     phone    699         1 2024-03-05
            cd     watch    349         2 2024-12-12
            ef    laptop   2599         3 2023-08-10
            gh      book     19         5 2024-01-13
            ij     watch    299         1 2022-07-20
            kl  keyboard     69         1 2023-05-08
            mn   glasses    129         2 2021-03-03
            op   battery     49         2 2024-11-07
            qr     mouse     29         3 2024-11-07
            >>> table += {  # The order of the keys does not matter.
            ...     "Product": "screen",
            ...     "Quantity": 1,
            ...     "Price": 599,
            ...     "Date": date(2023, 5, 8),
            ...     "ID": "st",
            ... }
            >>> table.head(10).sort_index()
                 Product  Price  Quantity       Date
            ID
            ab     phone    699         1 2024-03-05
            cd     watch    349         2 2024-12-12
            ef    laptop   2599         3 2023-08-10
            gh      book     19         5 2024-01-13
            ij     watch    299         1 2022-07-20
            kl  keyboard     69         1 2023-05-08
            mn   glasses    129         2 2021-03-03
            op   battery     49         2 2024-11-07
            qr     mouse     29         3 2024-11-07
            st    screen    599         1 2023-05-08

        See Also:
            :class:`~atoti.data_load.DataLoad`, :meth:`load_async`, :meth:`~atoti.tables.Tables.data_transaction`, and :meth:`~atoti.tables.Tables.infer_data_types`.

        """
        match data:
            case pa.Table():
                with tempfile.TemporaryDirectory() as directory:
                    path = pathlib.Path(directory) / "table.arrow"
                    write_arrow_to_file(data, filepath=path)
                    arrow_load = ArrowLoad(path)
                    return self.load(arrow_load)
            case pd.DataFrame():
                arrow_table = pandas_to_arrow(
                    data,
                    data_types={
                        column_name: self[column_name].data_type for column_name in self
                    },
                )
                return self.load(arrow_table)
            case DataLoad():
                return self._client._require_py4j_client().load_data_into_table(
                    data,
                    scenario_name=self.scenario,
                    table_identifier=self._identifier,
                )
            case _:
                assert_never(data)

    async def load_async(
        self,
        data: _LoadArgument,  # pyright: ignore[reportUnknownParameterType]
        /,
    ) -> None:
        """Load data into the table asynchronously.

        This is a non-blocking operation allowing to load data into one or more tables concurrently.

        Args:
            data: The data to load.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> table = session.create_table(
            ...     "Example",
            ...     data_types={"key": "int", "value": "int"},
            ...     keys={"key"},
            ... )
            >>> df_1 = pd.DataFrame({"key": [1, 2], "value": [10, 20]})
            >>> df_2 = pd.DataFrame({"key": [3, 4], "value": [30, 40]})
            >>> df_3 = pd.DataFrame({"key": [2, 5], "value": [200, 500]})

            Loading two DataFrames concurrently:

            >>> import asyncio
            >>> async def load_df_1_and_2_concurrently(table):
            ...     await asyncio.gather(
            ...         table.load_async(df_1),
            ...         table.load_async(df_2),
            ...     )
            >>> asyncio.run(load_df_1_and_2_concurrently(table))
            >>> table.head().sort_index()
                 value
            key
            1       10
            2       20
            3       30
            4       40
            >>> table.drop()

            Loading two DataFrames sequentially:

            >>> async def load_df_1_and_3_sequentially(table):
            ...     await table.load_async(df_1)
            ...     assert table.row_count == 2
            ...     await table.load_async(df_3)
            ...     assert table.row_count == 3, (
            ...         "df_3 should have overrode key `1` of df_1"
            ...     )
            >>> asyncio.run(load_df_1_and_3_sequentially(table))
            >>> table.head().sort_index()
                 value
            key
            1       10
            2      200
            5      500
            >>> table.drop()

            Loading three DataFrames in a concurrent and sequential mix:

            >>> async def load_df_1_and_3_sequentially_bis(table):
            ...     await table.load_async(df_1)
            ...     assert table.row_count >= 2
            ...     await table.load_async(df_3)
            ...     assert table.row_count >= 3
            >>> async def load_df_2(table):
            ...     await table.load_async(df_2)
            ...     assert table.row_count >= 2
            >>> async def load_all(table):
            ...     await asyncio.gather(
            ...         load_df_1_and_3_sequentially_bis(table),
            ...         load_df_2(table),
            ...     )
            ...     assert table.row_count == 5
            >>> asyncio.run(load_all(table))
            >>> table.head().sort_index()
                 value
            key
            1       10
            2      200
            3       30
            4       40
            5      500

        See Also:
            :meth:`load` and :meth:`~atoti.tables.Tables.data_transaction`.

        """
        await to_thread(self.load, data)

    @deprecated(
        "`table.load_csv(path)` is deprecated, use `table.load(tt.CsvLoad(path))` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def load_csv(
        self,
        path: pathlib.Path | str,
        /,
        *,
        columns: Mapping[str, str] | Sequence[str] = frozendict(),
        separator: str | None = ",",
        encoding: str = "utf-8",
        process_quotes: bool | None = True,
        array_separator: str | None = None,
        date_patterns: Mapping[str, str] = frozendict(),
        client_side_encryption: ClientSideEncryptionConfig | None = None,
        **kwargs: Any,
    ) -> None:
        """Load a CSV into this scenario.

        :meta private:
        """
        self.load(
            CsvLoad(
                path,
                columns=columns,
                separator=separator,
                encoding=encoding,
                process_quotes=process_quotes,
                array_separator=array_separator,
                date_patterns=date_patterns,
                client_side_encryption=client_side_encryption,
                **kwargs,
            ),
        )

    @deprecated(
        "`table.load_pandas(dataframe)` is deprecated, use `table.load(dataframe)` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def load_pandas(
        self,
        dataframe: pd.DataFrame,
        /,
    ) -> None:
        """Load a pandas DataFrame into this scenario.

        :meta private:
        """
        self.load(dataframe)

    @deprecated(
        "`table.load_arrow(arrow_table)` is deprecated, use `table.load(arrow_table)` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def load_arrow(
        self,
        table: pa.Table,  # pyright: ignore[reportUnknownParameterType]
        /,
    ) -> None:
        """Load an Arrow Table into this scenario.

        :meta private:
        """
        self.load(table)

    @deprecated(
        "`table.load_numpy(array)` is deprecated, use `table.load(pd.DataFrame(array, columns=list(self)))` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def load_numpy(
        self,
        array: NDArray[Any],
        /,
    ) -> None:
        """Load a NumPy 2D array into this scenario.

        :meta private:
        """
        dataframe = pd.DataFrame(array, columns=list(self))
        self.load(dataframe)

    @deprecated(
        "`table.load_parquet(path)` is deprecated, use `table.load(tt.ParquetLoad(path))` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def load_parquet(
        self,
        path: pathlib.Path | str,
        /,
        *,
        columns: Mapping[str, str] = frozendict(),
        client_side_encryption: ClientSideEncryptionConfig | None = None,
    ) -> None:
        """Load a Parquet file into this scenario.

        :meta private:
        """
        self.load(
            ParquetLoad(
                path,
                columns=columns,
                client_side_encryption=client_side_encryption,
            ),
        )

    @deprecated(
        "`table.load_spark(dataframe)` is deprecated, use `table.load(dataframe.toPandas())` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def load_spark(
        self,
        dataframe: SparkDataFrame,
        /,
    ) -> None:
        """Load a Spark DataFrame into this scenario.

        :meta private:
        """
        # Converting the Spark DataFrame to an in-memory pandas DataFrame instead of exporting to a Parquet file.
        # See https://activeviam.atlassian.net/browse/PYTHON-456.
        pandas_dataframe = dataframe.toPandas()
        self.load(pandas_dataframe)

    @deprecated(
        "`table.load_kafka(...)` is deprecated, use `table.stream(atoti_kafka.KafkaStream(...))` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def load_kafka(
        self,
        bootstrap_server: str,
        topic: str,
        *,
        group_id: str,
        batch_duration: Duration = timedelta(seconds=1),
        consumer_config: Mapping[str, str] = frozendict(),
    ) -> None:
        """Load a Kafka stream into this scenario.

        :meta private:
        """
        from atoti_kafka import (  # pylint: disable=nested-import,undeclared-dependency
            KafkaStream,
        )

        kafka_stream = KafkaStream(
            bootstrap_server,
            topic,
            group_id,
            batch_duration=batch_duration,
            consumer_config=consumer_config,
        )
        self.stream(kafka_stream)

    @deprecated(
        "`table.load_sql(query)` is deprecated, use `table.load(atoti_jdbc.JdbcLoad(query))` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def load_sql(
        self,
        sql: str,
        *,
        driver: str | None = None,
        parameters: Sequence[Constant] = (),
        url: str,
    ) -> None:
        """Load the result of a SQL query into this scenario.

        :meta private:
        """
        from atoti_jdbc import (  # pylint: disable=nested-import,undeclared-dependency
            JdbcLoad,
        )

        jdbc_load = JdbcLoad(sql, driver=driver, parameters=parameters, url=url)
        return self.load(jdbc_load)

    def stream(self, data: DataStream, /) -> None:
        """Stream data into the table."""
        self._client._require_py4j_client().load_data_into_table(
            data,
            scenario_name=self.scenario,
            table_identifier=self._identifier,
        )

    def query(
        self,
        *columns: Column,
        filter: TableQueryFilterCondition  # noqa: A002
        | None = None,
        max_rows: PositiveInt = (_JAVA_INT_RANGE.stop - 1) - 1,
        timeout: Duration = _DEFAULT_QUERY_TIMEOUT,
    ) -> pd.DataFrame:
        """Query the table to retrieve some of its rows.

        If the table has more than *max_rows* rows matching *filter*, the set of returned rows is unspecified and can change from one call to another.

        As opposed to :meth:`head`, the returned DataFrame will not be indexed by the table's :attr:`keys` since *columns* may lack some of them.

        Args:
            columns: The columns to query.
                If empty, all the columns of the table will be queried.
            filter: The filtering condition.
                Only rows matching this condition will be returned.
            max_rows: The maximum number of rows to return.
            timeout: The duration the query execution can take before being aborted.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["Continent", "Country", "Currency", "Price"],
            ...     data=[
            ...         ("Europe", "France", "EUR", 200.0),
            ...         ("Europe", "Germany", "EUR", 150.0),
            ...         ("Europe", "United Kingdom", "GBP", 120.0),
            ...         ("America", "United states", "USD", 240.0),
            ...         ("America", "Mexico", "MXN", 270.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(
            ...     df,
            ...     keys={"Continent", "Country", "Currency"},
            ...     table_name="Prices",
            ... )
            >>> result = table.query(filter=table["Price"] >= 200)
            >>> result.set_index(list(table.keys)).sort_index()
                                              Price
            Continent Country       Currency
            America   Mexico        MXN       270.0
                      United states USD       240.0
            Europe    France        EUR       200.0

        """
        if not columns:
            columns = tuple(self[column_name] for column_name in self)

        for column in columns:
            column_table_name = column._identifier.table_identifier.table_name
            if column_table_name != self.name:
                raise ValueError(
                    f"Expected all columns to be from table `{self.name}` but got column `{column.name}` from table `{column_table_name}`.",
                )

        return execute_query(
            client=self._client,
            column_definitions=[
                ColumnDefinition(
                    name=column.name,
                    data_type=column.data_type,
                    nullable=column.default_value is None,
                )
                for column in columns
            ],
            filter=filter,
            max_rows=max_rows,
            scenario_name=self.scenario,
            table_name=self.name,
            timeout=timeout,
        )


@final
class _TableScenarios:
    def __init__(self, identifier: TableIdentifier, /, *, client: Client) -> None:
        self._client: Final = client
        self.__identifier: Final = identifier

    def __getitem__(self, name: str, /) -> Table:
        """Get the scenario or create it if it does not exist."""
        return Table(self.__identifier, client=self._client, scenario=name)

    def __delitem__(self, name: str, /) -> None:
        raise RuntimeError(
            "You cannot delete a scenario from a table since they are shared between all tables."
            "Use the Session.delete_scenario() method instead.",
        )
