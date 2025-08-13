from __future__ import annotations

from collections.abc import (
    Callable,
    Collection,
    Mapping,
    MutableMapping,
    Sequence,
    Set as AbstractSet,
)
from contextlib import AbstractContextManager, ExitStack, suppress
from datetime import datetime, timedelta
from pathlib import Path
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Final,
    Literal,
    TypeAlias,
    cast,
    final,
    overload,
)
from urllib.parse import urlparse
from warnings import warn

import httpx
import pandas as pd
import pyarrow as pa
from numpy.typing import NDArray
from pydantic import Field, JsonValue, SkipValidation
from typing_extensions import NotRequired, Self, TypedDict, Unpack, deprecated, override

from ._basic_credentials import BasicCredentials
from ._client import Client
from ._client._get_authentication_headers import get_authentication_headers
from ._collections import frozendict
from ._constant import Constant
from ._content_client import SECURITY_ROOT_DIRECTORY as _SECURITY_ROOT_DIRECTORY
from ._cube_definition import CubeDefinition
from ._cube_discovery import get_discovery
from ._cube_filter_condition import CubeFilterCondition
from ._data_type import DataType
from ._default_query_timeout import DEFAULT_QUERY_TIMEOUT as _DEFAULT_QUERY_TIMEOUT
from ._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from ._doc import doc
from ._docs_utils import QUERY_KWARGS as _QUERY_KWARGS
from ._identification import (
    ColumnName,
    IdentifierT_co,
    TableIdentifier,
    TableName,
    UserName,
)
from ._ipython import find_corresponding_top_level_variable_name
from ._link import Link
from ._mdx_query import Context, execute_query, explain_query
from ._pandas_utils import pandas_to_arrow
from ._session_id import SessionId, generate_session_id
from ._session_resources import connected_session_client, started_session_resources
from ._table_definition import TableDefinition
from ._transaction import (
    TRANSACTION_DOC_KWARGS as _TRANSACTION_DOC_KWARGS,
    transact_data_model,
)
from ._typing import Duration
from ._widget import Widget
from .authentication import Authenticate, ClientCertificate
from .client_side_encryption_config import ClientSideEncryptionConfig
from .config import SessionConfig
from .cube import Cube
from .cubes import Cubes
from .data_load import CsvLoad, ParquetLoad
from .data_load._split_globfree_absolute_path_and_glob_pattern import (
    split_globfree_absolute_path_and_glob_pattern,
)
from .directquery import (
    ExternalAggregateTable,
    ExternalDatabaseConnection,
    ExternalTable,
    MultiColumnArrayConversion,
)
from .directquery._external_aggregate_table._external_aggregate_tables import (
    ExternalAggregateTables,
)
from .directquery._external_database_connection_config import (
    ExternalDatabaseConnectionConfigT,
)
from .directquery._external_table_config import (
    ArrayConversionConfig,
    ExternalTableConfig,
)
from .distribution.clusters import Clusters
from .endpoint import (  # pylint: disable=shortest-import
    Request as Request,
)
from .endpoint._http_method import HttpMethod
from .endpoint._server import Server as EndpointServer
from .mdx_query_result import MdxQueryResult
from .proxy import Proxy
from .security import Security
from .table import Table
from .tables import Tables
from .user import User

if TYPE_CHECKING:
    # pylint: disable=nested-import,undeclared-dependency
    from _atoti_server import ServerSubprocess

    # pyspark is an optional dependency.
    # pylint: disable=nested-import,undeclared-dependency
    from pyspark.sql import DataFrame as SparkDataFrame
else:
    ServerSubprocess = object
    SparkDataFrame = object

_EndpointCallback: TypeAlias = Callable[[Request, User, "Session"], JsonValue]

_DEFAULT_LICENSE_MINIMUM_REMAINING_TIME = timedelta(days=7)


class _TablePrivateParameters(TypedDict):  # pylint: disable=final-class
    types: NotRequired[Mapping[str, DataType]]


def _get_data_types(
    data_types: Mapping[ColumnName, DataType],
    /,
    **kwargs: Unpack[_TablePrivateParameters],
) -> Mapping[ColumnName, DataType]:
    deprecated_data_types = kwargs.get("types")
    if deprecated_data_types is not None:
        warn(
            "The `types` parameter is deprecated, use `data_types` instead.",
            category=_DEPRECATED_WARNING_CATEGORY,
            stacklevel=2,
        )
        return deprecated_data_types
    return data_types


@final
class _ReadArrowPrivateParameters(_TablePrivateParameters): ...


@final
class _ReadCsvPrivateParameters(_TablePrivateParameters):
    parser_thread_count: NotRequired[int]
    buffer_size_kb: NotRequired[int]


@final
class _ReadPandasPrivateParameters(_TablePrivateParameters): ...


@final
class _ReadParquetPrivateParameters(_TablePrivateParameters): ...


@final
class _StartPrivateParameters(TypedDict):
    address: NotRequired[str]
    enable_py4j_auth: NotRequired[bool]
    py4j_server_port: NotRequired[int]
    debug: NotRequired[bool]
    debug_id: NotRequired[str]
    "Value of the ``--debug-id`` parameter passed to the ``ApplicationStarter`` to connect to."
    session_config_path: NotRequired[Path | str]
    port_path: NotRequired[Path | str]
    api_token: NotRequired[str]  # Used by Atoti Platform


@deprecated(
    "Inferring `table_name` from `path` is deprecated, pass a `table_name` argument instead.",
    category=_DEPRECATED_WARNING_CATEGORY,
    stacklevel=2,
)
def _infer_table_name(path: Path | str, /, *, extension: str) -> TableName:
    globfree_absolute_path, glob_pattern = (
        split_globfree_absolute_path_and_glob_pattern(
            path,
            extension=extension,
        )
    )
    if glob_pattern is not None:
        raise ValueError("Cannot infer `table_name` from glob pattern `path`.")
    return Path(globfree_absolute_path).stem.capitalize()


@final
class Session(AbstractContextManager["Session"]):
    """The entry point to interact with Atoti applications.

    A session holds data in :attr:`~atoti.Session.tables` and aggregates it in :attr:`~atoti.Session.cubes`.
    It also serves a web app for data exploration accessible with :attr:`~link`.

    It can be created with either :meth:`start` or :meth:`connect`.
    """

    def __init__(
        self,
        *,
        auto_join_clusters: bool,
        client: Client,
        server_subprocess: ServerSubprocess | None,
        session_id: SessionId,
    ):
        self._auto_join_clusters: Final = auto_join_clusters
        self._client: Final = client
        self._exit_stack: Final = ExitStack()
        self._endpoint_server: Final = self._exit_stack.push(
            EndpointServer(session_url=self._client._url),
        )
        self._id: Final = session_id
        self.__server_subprocess: Final = server_subprocess

    @classmethod
    def connect(
        cls,
        url: str,
        *,
        authentication: Annotated[Authenticate, SkipValidation]
        | ClientCertificate
        | None = None,
        certificate_authority: Path | None = None,
    ) -> Self:
        """Connect to an existing session.

        Here is a breakdown of the *Live extension* capabilities of the returned session:

        .. _local:

        * Local

          * If all the following conditions are met:

            .. _a:

            * a) the target session requires authentication (e.g. it has :attr:`~atoti.SessionConfig.security` configured)

            .. _b:

            * b) the provided *authentication* or *certificate_authority* arguments grant :guilabel:`ROLE_ADMIN`

            .. _c:

            * c) the target session (the one at *url*) was :meth:`started <start>` with the same version of Atoti Python SDK (|version|)

            .. _d:

            * d) the target session runs on the same host as the current Python process

          * Then all :class:`Session` capabilities can be used except for:

            * :meth:`endpoint`
            * :attr:`logs_path`
            * :meth:`wait`

        .. _remote:

        * Remote

          * If conditions :ref:`a. <a>`, :ref:`b. <b>`, and :ref:`c. <c>` are met but not :ref:`d. <d>` (i.e., not on the same host)
          * Then all :ref:`local <local>` capabilities are available except those needing a shared file system.
            For example:

            * :meth:`~atoti.Table.load` with :class:`~atoti.CsvLoad` or :class:`~atoti.ParquetLoad`, :meth:`read_csv`, and :meth:`read_parquet` are not available (unless loading from :ref:`cloud storage <getting_started/plugins:Cloud storage>`)
            * :meth:`~atoti.Table.load` with :class:`pyarrow.Table` or :class:`pandas.DataFrame`, :meth:`read_arrow` and :meth:`read_pandas` methods are not available

        * No security management

          * If conditions :ref:`a. <a>` and :ref:`b. <b>` are meet, plus both:

            .. _e:

            * e) the target session runs the same Atoti Server version (e.g. |atoti_server_version| for Atoti Python SDK |version|)

            .. _f:

            * f) the target session :atoti_server_docs:`is exposed to Atoti Python SDK <starters/how-to/expose-app-to-python/>`

          * Depending on whether :ref:`d. <d>` is met, either :ref:`local <local>` or :ref:`remote <remote>` capabilities are available, except for :attr:`security` management features.

        * Read-only

          * If only condition :ref:`e. <e>` is met (i.e. matching Atoti Server versions)
          * Then capabilities that modify the session data or data model are unavailable.
            However, some read-only capabilities remain accessible.
            For example:

            * Not available: :meth:`create_table`, :meth:`create_cube`, and :meth:`read_csv`
            * Available: :attr:`atoti.tables.Tables.schema` and :meth:`atoti.Table.query`

        * Minimal capabilities

          * Always available:

            * :attr:`atoti.Session.link`
            * :attr:`atoti.Session.query_mdx`
            * :attr:`atoti.Cube.query`

        Note:
            Data and data model changes made from a connected session are not persisted on the target session.
            They will be lost if the target session is restarted.

        Args:
            url: The base URL of the target session.
                The endpoint ``f"{url}/versions/rest"`` is expected to exist.
            authentication: The method used to authenticate against the target session.
            certificate_authority: Path to the custom certificate authority file to use to verify the HTTPS connection.
                Required when the target session has been configured with an SSL certificate that is not signed by some trusted public certificate authority.

        Example:
            >>> session_config = tt.SessionConfig(security=tt.SecurityConfig())
            >>> secure_session = tt.Session.start(session_config)
            >>> _ = secure_session.create_table("Example", data_types={"Id": "String"})
            >>> secure_session.security.individual_roles.update(
            ...     {"user": {"ROLE_USER"}, "admin": {"ROLE_USER", "ROLE_ADMIN"}},
            ... )
            >>> password = "passwd"
            >>> secure_session.security.basic_authentication.credentials.update(
            ...     {"user": password, "admin": password}
            ... )
            >>> admin_session = tt.Session.connect(
            ...     secure_session.url,
            ...     authentication=tt.BasicAuthentication("admin", password),
            ... )
            >>> table = admin_session.tables["Example"]
            >>> table += ("foo",)
            >>> table.head()
                Id
            0  foo

            .. doctest::
                :hide:

                >>> del admin_session

            Live extension requires the connected session to be granted :guilabel:`ROLE_ADMIN`:

            >>> user_session = tt.Session.connect(
            ...     secure_session.url,
            ...     authentication=tt.BasicAuthentication("user", password),
            ... )
            >>> user_session.ready = False  # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            RuntimeError: This Live Extension action is not available...

            .. doctest::
                :hide:

                >>> del user_session
                >>> del secure_session

            Live extension requires the target session to be secure:

            >>> unsecure_session = tt.Session.start()
            >>> _ = unsecure_session.create_table(
            ...     "Example", data_types={"Id": "String"}
            ... )
            >>> connected_session = tt.Session.connect(unsecure_session.url)
            >>> connected_session.ready = False  # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            RuntimeError: This Live Extension action is not available...

            .. doctest::
                :hide:

                >>> del connected_session
                >>> del unsecure_session

        See Also:
            :meth:`start`
        """
        session_id = generate_session_id()

        with ExitStack() as exit_stack:
            client = exit_stack.enter_context(
                connected_session_client(
                    url,
                    authentication=authentication,
                    certificate_authority=certificate_authority,
                    session_id=session_id,
                ),
            )
            session = cls(
                auto_join_clusters=True,
                client=client,
                server_subprocess=None,
                session_id=session_id,
            )
            session._exit_stack.push(exit_stack.pop_all())
            return session

    @classmethod
    def _connect(
        cls,
        address: str,
        /,
        *,
        py4j_server_port: int | None = None,
    ) -> Self:
        with ExitStack() as exit_stack:
            client, server_subprocess, session_id = exit_stack.enter_context(
                started_session_resources(
                    address=address,
                    config=SessionConfig(),
                    distributed=False,
                    enable_py4j_auth=False,
                    py4j_server_port=py4j_server_port,
                    debug=False,
                    debug_id=None,
                    session_config_path=None,
                    port_path=None,
                    api_token=None,
                ),
            )
            session = cls(
                auto_join_clusters=True,
                client=client,
                server_subprocess=server_subprocess,
                session_id=session_id,
            )
            session._exit_stack.push(exit_stack.pop_all())
            return session

    @classmethod
    def start(
        cls,
        config: SessionConfig | None = None,
        /,
        **kwargs: Unpack[_StartPrivateParameters],
    ) -> Self:
        """Start a new Atoti server subprocess and connect to it.

        If the :guilabel:`JAVA_HOME` environment variable is not defined or if it points to an unsupported Java version, the JVM from `jdk4py <https://github.com/activeviam/jdk4py>`__ will be used instead.

        Args:
            config: The config of the session.

        See Also:
            :meth:`connect`
        """
        if config is None:
            config = SessionConfig()

        with ExitStack() as exit_stack:
            client, server_subprocess, session_id = exit_stack.enter_context(
                started_session_resources(
                    address=kwargs.get("address"),
                    config=config,
                    distributed=False,
                    # Enabling authentication by default makes it easy to detect an existing detached process: if an unauthenticated connection can be made on Py4J's default port it means it's a detached process.
                    enable_py4j_auth=kwargs.get("enable_py4j_auth", True),
                    py4j_server_port=kwargs.get("py4j_server_port"),
                    debug=kwargs.get("debug", False),
                    debug_id=kwargs.get("debug_id"),
                    session_config_path=kwargs.get("session_config_path"),
                    port_path=kwargs.get("port_path"),
                    api_token=kwargs.get("api_token"),
                ),
            )
            session = cls(
                auto_join_clusters=True,
                client=client,
                server_subprocess=server_subprocess,
                session_id=session_id,
            )
            session._warn_if_license_about_to_expire()

            for plugin in config.plugins.values():
                plugin.session_hook(session)

            session._exit_stack.push(exit_stack.pop_all())
            return session

    @override
    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        exception_traceback: TracebackType | None,
    ) -> None:
        self._exit_stack.__exit__(exception_type, exception_value, exception_traceback)

    def close(self) -> None:
        """Close this session and free all associated resources.

        The session cannot be used after calling this method.

        Closing a session frees its port so it can be reused by another session or another process.

        This method is called by the ``__del__()`` method so garbage collected sessions will automatically be closed.
        Python synchronously garbage collects objects as soon as their last (hard) reference is lost.
        In a notebook, it is thus possible to run the following cell multiple times without encountering a "port already in use" error:

        .. code-block:: python

            # (Re)assigning the `session` variable to garbage collect previous reference (if any).
            session = None
            # If a previous `session` was using port 1337, it is now free to use again (unless another process just took it).
            session = tt.Session.start(tt.SessionConfig(port=1337))

        Note:
            In a notebook, evaluating/printing an object creates long lasting references to it preventing the object from being garbage collected.
            The pattern shown above will thus only work if the `session` object was not used as the last expression of a cell.

        """
        self.__exit__(None, None, None)

    def __del__(self) -> None:
        # Use private method to avoid sending a telemetry event that would raise `RuntimeError: cannot schedule new futures after shutdown` when calling `ThreadPoolExecutor.submit()`.
        self.__exit__(None, None, None)

    @property
    def _server_subprocess(self) -> ServerSubprocess:
        if self.__server_subprocess is None:
            raise RuntimeError("This session did not start the server subprocess.")
        return self.__server_subprocess

    @property
    def logs_path(self) -> Path:
        """Path to the session logs file."""
        return self._server_subprocess.logs_path

    @property
    def cubes(self) -> Cubes:
        """The cubes in this session."""
        return Cubes(
            client=self._client,
            get_widget_creation_code=self._get_widget_creation_code,
            session_id=self._id,
        )

    @property
    def tables(self) -> Tables:
        return Tables(client=self._client, session_id=self._id)

    @property
    def clusters(self) -> Clusters:
        """The clusters that this session contribute to."""
        return Clusters(
            client=self._client,
            trigger_auto_join=(lambda: self.ready)
            if self._auto_join_clusters
            else (lambda: False),
        )

    def create_table(
        self,
        name: str,
        *,
        # Make this parameter mandatory when removing the deprecated `types` parameter.
        data_types: Mapping[ColumnName, DataType] = frozendict(),
        default_values: Mapping[ColumnName, Constant | None] = frozendict(),
        keys: AbstractSet[ColumnName] | Sequence[ColumnName] = frozenset(),
        partitioning: str | None = None,
        **kwargs: Unpack[_TablePrivateParameters],
    ) -> Table:
        """Create an empty table with columns of the given *data_types*.

        Args:
            name: The name of the table to create.
            data_types: The table column names and their corresponding :mod:`data type <atoti.type>`.
            default_values: Mapping from column name to column :attr:`~atoti.Column.default_value`.
            keys: The columns that will become :attr:`~atoti.Table.keys` of the table.

                If a :class:`~collections.abc.Set` is given, the keys will be ordered as the table columns.
            partitioning: The definition of how the data will be split across partitions.

                Default rules:

                * Only non-joined tables are automatically partitioned.
                * Tables are automatically partitioned by hashing their key columns.
                  If there are no key columns, all the dictionarized columns are hashed.
                * Joined tables can only use a sub-partitioning of the table referencing them.
                * Automatic partitioning is done modulo the number of available cores.

                For instance, ``"modulo4(country)"`` splits the data across 4 partitions based on the :guilabel:`country` column's dictionarized value.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> from datetime import date
            >>> table = session.create_table(
            ...     "Product",
            ...     data_types={
            ...         "Date": "LocalDate",
            ...         "Product": "String",
            ...         "Quantity": "double",
            ...     },
            ...     keys={"Product", "Date"},
            ... )
            >>> table.head()
            Empty DataFrame
            Columns: [Quantity]
            Index: []
            >>> {column_name: table[column_name].data_type for column_name in table}
            {'Date': 'LocalDate', 'Product': 'String', 'Quantity': 'double'}
            >>> table.keys
            ('Date', 'Product')

        """
        data_types = _get_data_types(data_types, **kwargs)
        definition = TableDefinition(
            data_types=data_types,
            default_values=default_values,
            keys=keys,
            partitioning=partitioning,
        )
        return self.tables.set(name, definition)

    def connect_to_external_database(
        self,
        connection_config: ExternalDatabaseConnectionConfigT,
        /,
    ) -> ExternalDatabaseConnection[ExternalDatabaseConnectionConfigT]:
        """Connect to an external database using DirectQuery.

        Note:
            This feature is not part of the community edition: it needs to be :doc:`unlocked </guides/unlocking_all_features>`.

        Args:
            connection_config: The config to connect to the external database.
                Each :ref:`DirectQuery plugin <getting_started/plugins:DirectQuery>` has its own ``ConnectionConfig`` class.
        """
        self._client._require_py4j_client().connect_to_database(
            connection_config._database_key,
            url=connection_config._url,
            password=connection_config._password,
            options=connection_config._options,
        )
        return ExternalDatabaseConnection(
            client=self._client,
            database_key=connection_config._database_key,
        )

    def add_external_table(
        self,
        external_table: ExternalTable[ExternalDatabaseConnectionConfigT],
        /,
        table_name: str | None = None,
        *,
        columns: Mapping[str, str] = frozendict(),
        config: ExternalTableConfig[ExternalDatabaseConnectionConfigT] | None = None,
    ) -> Table:
        """Add a table from an external database to the session.

        Args:
            external_table: The external database table from which to build the session table.
                Instances of such tables are obtained through an external database connection.
            table_name: The name to give to the table in the session.
                If ``None``, the name of the external table is used.
            columns: Mapping from external column names to local column names.
                If empty, the local columns will share the names of the external columns.
            config: The config to add the external table.
                Each :ref:`DirectQuery plugin <getting_started/plugins:DirectQuery>` has its own ``TableConfig`` class.

        Example:
            .. doctest::
                :hide:

                >>> import os
                >>> from atoti_directquery_snowflake import ConnectionConfig
                >>> connection_config = ConnectionConfig(
                ...     url="jdbc:snowflake://"
                ...     + os.environ["SNOWFLAKE_ACCOUNT_IDENTIFIER"]
                ...     + ".snowflakecomputing.com/?user="
                ...     + os.environ["SNOWFLAKE_USERNAME"]
                ...     + "&database=TEST_RESOURCES"
                ...     + "&schema=TESTS",
                ...     password=os.environ["SNOWFLAKE_PASSWORD"],
                ... )
                >>> session = getfixture("session_with_directquery_snowflake_plugin")

            >>> external_database = session.connect_to_external_database(
            ...     connection_config
            ... )
            >>> external_table = external_database.tables["TUTORIAL", "SALES"]
            >>> list(external_table)
            ['SALE_ID', 'DATE', 'SHOP', 'PRODUCT', 'QUANTITY', 'UNIT_PRICE']

            Add the external table, filtering out some columns and renaming the remaining ones:

            >>> from atoti_directquery_snowflake import TableConfig
            >>> table = session.add_external_table(
            ...     external_table,
            ...     columns={
            ...         "SALE_ID": "Sale ID",
            ...         "DATE": "Date",
            ...         "PRODUCT": "Product",
            ...         "QUANTITY": "Quantity",
            ...     },
            ...     config=TableConfig(keys={"Sale ID"}),
            ...     table_name="sales_renamed",
            ... )
            >>> table.head().sort_index()
                          Date Product  Quantity
            Sale ID
            S0007   2022-02-01   BED_2       1.0
            S0008   2022-01-31   BED_2       1.0
            S0009   2022-01-31   BED_2       1.0
            S0010   2022-01-31   BED_2       3.0
            S0019   2022-02-02   HOO_5       1.0

        """
        if table_name is None:
            table_name = external_table._identifier.table_name

        array_conversion = None
        clustering_columns = None
        keys = None
        emulated_time_travel = None

        if config is not None:
            if isinstance(config, ArrayConversionConfig):
                array_conversion = config.array_conversion

            clustering_columns = (
                frozenset(config.clustering_columns)
                if config.clustering_columns
                else None
            )
            keys = tuple(config.keys) if config.keys else None
            emulated_time_travel = config.time_travel

        py4j_client = self._client._require_py4j_client()

        if array_conversion is not None:
            if isinstance(array_conversion, MultiColumnArrayConversion):
                py4j_client.add_external_multi_column_array_table(
                    external_table._database_key,
                    column_prefixes=array_conversion.column_prefixes,
                    clustering_columns=clustering_columns
                    if clustering_columns
                    else None,
                    columns=columns,
                    identifier=external_table._identifier,
                    keys=keys,
                    local_table_identifier=TableIdentifier(table_name),
                    emulated_time_travel=emulated_time_travel,
                )
            else:
                py4j_client.add_external_table_with_multi_row_arrays(
                    external_table._database_key,
                    array_columns=array_conversion.array_columns,
                    clustering_columns=clustering_columns,
                    identifier=external_table._identifier,
                    index_column=array_conversion.index_column,
                    local_table_identifier=TableIdentifier(table_name),
                    columns=columns,
                    emulated_time_travel=emulated_time_travel,
                )
        else:
            # Table without conversion
            py4j_client.add_external_table(
                external_table._database_key,
                clustering_columns=clustering_columns,
                columns=columns,
                identifier=external_table._identifier,
                keys=keys,
                local_table_identifier=TableIdentifier(table_name),
                emulated_time_travel=emulated_time_travel,
            )

        py4j_client.refresh()

        return self.tables[table_name]

    def _synchronize_with_external_database(self) -> None:
        self._client._require_py4j_client().synchronize_with_external_database()

    @property
    def _external_aggregate_tables(self) -> MutableMapping[str, ExternalAggregateTable]:
        return ExternalAggregateTables(client=self._client)

    def read_pandas(
        self,
        dataframe: pd.DataFrame,
        /,
        *,
        data_types: Mapping[str, DataType] = frozendict(),
        default_values: Mapping[str, Constant | None] = frozendict(),
        keys: AbstractSet[str] | Sequence[str] = frozenset(),
        partitioning: str | None = None,
        table_name: str,
        **kwargs: Unpack[_ReadPandasPrivateParameters],
    ) -> Table:
        """Read a pandas DataFrame into a table.

        Note:
            This is just a shortcut for:

            .. code-block:: python

                inferred_data_types = session.tables.infer_data_types(dataframe)
                table = session.create_table(
                    table_name,
                    data_types={**inferred_data_types, **data_types},
                    default_values=...,
                    keys=...,
                    partitioning=...,
                )
                table.load(dataframe)

            The longer version unlocks better performance because it can be split to move the :meth:`~atoti.Table.load` call inside a :meth:`~atoti.tables.Tables.data_transaction`.

        All the named indices of the DataFrame are included into the table.
        Multilevel columns are flattened into a single string name.

        Args:
            data_types: Data types for some or all columns of the table.
                Data types for non specified columns will be inferred from the dataframe dtypes.
            dataframe: The DataFrame to load.
            default_values: See :meth:`create_table`'s *default_values*.
            keys: See :meth:`create_table`'s *keys*.
            partitioning: See :meth:`create_table`'s *partitioning*.
            table_name: See :meth:`create_table`'s *name*.

        """
        data_types = _get_data_types(
            data_types, **cast(_TablePrivateParameters, kwargs)
        )
        arrow_table = pandas_to_arrow(dataframe, data_types=data_types)
        return self.read_arrow(
            arrow_table,
            data_types=data_types,
            default_values=default_values,
            keys=keys,
            partitioning=partitioning,
            table_name=table_name,
        )

    def read_arrow(
        self,
        arrow_table: pa.Table,  # pyright: ignore[reportUnknownParameterType]
        /,
        *,
        data_types: Mapping[str, DataType] = frozendict(),
        default_values: Mapping[str, Constant | None] = frozendict(),
        keys: AbstractSet[str] | Sequence[str] = frozenset(),
        partitioning: str | None = None,
        table_name: str,
        **kwargs: Unpack[_ReadArrowPrivateParameters],
    ) -> Table:
        """Read an Arrow table into an Atoti table.

        Note:
            This is just a shortcut for:

            .. code-block:: python

                inferred_data_types = session.tables.infer_data_types(arrow_table)
                table = session.create_table(
                    table_name,
                    data_types={**inferred_data_types, **data_types},
                    default_values=...,
                    keys=...,
                    partitioning=...,
                )
                table.load(arrow_table)

            The longer version unlocks better performance because it can be split to move the :meth:`~atoti.Table.load` call inside a :meth:`~atoti.tables.Tables.data_transaction`.

        Args:
            arrow_table: The Arrow Table to load.
            data_types: Data types for some or all columns of the table.
                Data types for non specified columns will be inferred from the dataframe dtypes.
            default_values: See :meth:`create_table`'s *default_values*.
            keys: See :meth:`create_table`'s *keys*.
            partitioning: See :meth:`create_table`'s *partitioning*.
            table_name: See :meth:`create_table`'s *name*.

        """
        data_types = _get_data_types(
            data_types, **cast(_TablePrivateParameters, kwargs)
        )
        inferred_data_types = self.tables.infer_data_types(arrow_table)
        data_types = {**inferred_data_types, **data_types}
        table = self.create_table(
            table_name,
            data_types=data_types,
            default_values=default_values,
            keys=keys,
            partitioning=partitioning,
        )
        table.load(arrow_table)
        return table

    @deprecated(
        "`Session.read_spark()` is deprecated, see changelog for alternative.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def read_spark(
        self,
        dataframe: SparkDataFrame,
        /,
        *,
        default_values: Mapping[str, Constant | None] = frozendict(),
        keys: AbstractSet[str] | Sequence[str] = frozenset(),
        partitioning: str | None = None,
        table_name: str,
    ) -> Table:
        """Read a Spark DataFrame into a table.

        :meta private:
        """
        # Converting the Spark DataFrame to an in-memory pandas DataFrame instead of exporting to a Parquet file.
        # See https://activeviam.atlassian.net/browse/PYTHON-456.
        pandas_dataframe = dataframe.toPandas()
        return self.read_pandas(
            pandas_dataframe,
            default_values=default_values,
            keys=keys,
            partitioning=partitioning,
            table_name=table_name,
        )

    def read_csv(
        self,
        path: Path | str,
        /,
        *,
        array_separator: str | None = None,
        client_side_encryption: ClientSideEncryptionConfig | None = None,
        columns: Mapping[str, ColumnName] | Sequence[ColumnName] = frozendict(),
        data_types: Mapping[ColumnName, DataType] = frozendict(),
        date_patterns: Mapping[ColumnName, str] = frozendict(),
        default_values: Mapping[ColumnName, Constant | None] = frozendict(),
        encoding: str = "utf-8",
        keys: AbstractSet[ColumnName] | Sequence[ColumnName] = frozenset(),
        partitioning: str | None = None,
        process_quotes: bool | None = True,
        separator: str | None = ",",
        table_name: TableName | None = None,
        true_values: AbstractSet[Any] = frozenset(),
        false_values: AbstractSet[Any] = frozenset(),
        **kwargs: Unpack[_ReadCsvPrivateParameters],
    ) -> Table:
        """Read a CSV file into a table.

        Note:
            This is just a shortcut for:

            .. code-block:: python

                csv_load = tt.CsvLoad(path, ...)
                data_types = session.tables.infer_data_types(csv_load)
                table = session.create_table(
                    table_name,
                    data_types={**inferred_data_types, **data_types},
                    default_values=...,
                    keys=...,
                    partitioning=...,
                )
                table.load(csv_load)

            The longer version unlocks better performance because it can be split to move the :meth:`~atoti.Table.load` call inside a :meth:`~atoti.tables.Tables.data_transaction`.

        Args:
            array_separator: See :attr:`atoti.CsvLoad.array_separator`.
            client_side_encryption: See :attr:`atoti.CsvLoad.client_side_encryption`.
            columns: See :attr:`atoti.CsvLoad.columns`.
            data_types: The data types for some or all columns of the table.
                Data types for non specified columns will be inferred from the first 1,000 lines.
            date_patterns: See :attr:`atoti.CsvLoad.date_patterns`.
            default_values: See :meth:`create_table`'s *default_values*.
            encoding: See :attr:`atoti.CsvLoad.encoding`.
            false_values: See :attr:`atoti.CsvLoad.false_values`.
            keys: See :meth:`create_table`'s *keys*.
            partitioning: See :meth:`create_table`'s *partitioning*.
            path: See :attr:`atoti.CsvLoad.path`.
            process_quotes: See :attr:`atoti.CsvLoad.process_quotes`.
            separator: See :attr:`atoti.CsvLoad.separator`.
            table_name: See :meth:`create_table`'s *name*.
            true_values: See :attr:`atoti.CsvLoad.true_values`.

        """
        data_types = _get_data_types(
            data_types, **cast(_TablePrivateParameters, kwargs)
        )

        if table_name is None:
            table_name = _infer_table_name(path, extension=".csv")  # pyright: ignore[reportDeprecated]

        csv_load = CsvLoad(
            path,
            array_separator=array_separator,
            buffer_size_kb=kwargs.get("buffer_size_kb"),
            client_side_encryption=client_side_encryption,
            columns=columns,
            date_patterns=date_patterns,
            encoding=encoding,
            parser_thread_count=kwargs.get("parser_thread_count"),
            process_quotes=process_quotes,
            separator=separator,
            true_values=true_values,
            false_values=false_values,
        )
        inferred_data_types = self.tables.infer_data_types(csv_load)
        data_types = {**inferred_data_types, **data_types}
        table = self.create_table(
            table_name,
            data_types=data_types,
            default_values=default_values,
            keys=keys,
            partitioning=partitioning,
        )
        table.load(csv_load)
        return table

    def read_parquet(
        self,
        path: Path | str,
        /,
        *,
        client_side_encryption: ClientSideEncryptionConfig | None = None,
        columns: Mapping[str, ColumnName] = frozendict(),
        data_types: Mapping[ColumnName, DataType] = frozendict(),
        default_values: Mapping[ColumnName, Constant | None] = frozendict(),
        keys: AbstractSet[ColumnName] | Sequence[ColumnName] = frozenset(),
        partitioning: str | None = None,
        table_name: TableName | None = None,
        **kwargs: Unpack[_ReadParquetPrivateParameters],
    ) -> Table:
        """Read a Parquet file into a table.

        Note:
            This is just a shortcut for:

            .. code-block:: python

                parquet_load = tt.ParquetLoad(path, ...)
                inferred_data_types = session.tables.infer_data_types(parquet_load)
                table = session.create_table(
                    table_name,
                    data_types={**inferred_data_types, **data_types},
                    default_values=...,
                    keys=...,
                    partitioning=...,
                )
                table.load(parquet_load)

            The longer version unlocks better performance because it can be split to move the :meth:`~atoti.Table.load` call inside a :meth:`~atoti.tables.Tables.data_transaction`.

        Args:
            client_side_encryption:  See :attr:`atoti.ParquetLoad.client_side_encryption`.
            columns: See :attr:`atoti.ParquetLoad.columns`.
            data_types: See :meth:`create_table`'s *data_types*.
            default_values: See :meth:`create_table`'s *default_values*.
            keys: See :meth:`create_table`'s *keys*.
            partitioning: See :meth:`create_table`'s *partitioning*.
            path: See :attr:`atoti.ParquetLoad.path`.
            table_name: See :meth:`create_table`'s *name*.

        """
        data_types = _get_data_types(
            data_types, **cast(_TablePrivateParameters, kwargs)
        )

        if table_name is None:
            table_name = Path(path).stem.capitalize()

        parquet_load = ParquetLoad(
            path,
            client_side_encryption=client_side_encryption,
            columns=columns,
        )
        inferred_data_types = self.tables.infer_data_types(parquet_load)
        data_types = {**inferred_data_types, **data_types}
        table = self.create_table(
            table_name,
            data_types=data_types,
            default_values=default_values,
            keys=keys,
            partitioning=partitioning,
        )
        table.load(parquet_load)
        return table

    @deprecated(
        "`Session.read_numpy()` is deprecated, see changelog for alternative.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def read_numpy(
        self,
        array: NDArray[Any],
        /,
        *,
        columns: Sequence[str],
        default_values: Mapping[str, Constant | None] = frozendict(),
        keys: AbstractSet[str] | Sequence[str] = frozenset(),
        partitioning: str | None = None,
        table_name: str,
        types: Mapping[str, DataType] = frozendict(),
    ) -> Table:
        """Read a NumPy 2D array into a new table.

        :meta private:
        """
        dataframe = pd.DataFrame(array, columns=list(columns))
        return self.read_pandas(
            dataframe,
            data_types=types,
            default_values=default_values,
            keys=keys,
            partitioning=partitioning,
            table_name=table_name,
        )

    @deprecated(
        "`Session.read_sql()` is deprecated, see changelog for alternative.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def read_sql(
        self,
        sql: str,
        /,
        *,
        default_values: Mapping[str, Constant | None] = frozendict(),
        driver: str | None = None,
        keys: AbstractSet[str] | Sequence[str] = frozenset(),
        parameters: Sequence[Constant] = (),
        partitioning: str | None = None,
        table_name: str,
        types: Mapping[str, DataType] = frozendict(),
        url: str,
    ) -> Table:
        """Create a table from the result of the passed SQL query.

        :meta private:
        """
        # pylint: disable=nested-import,undeclared-dependency
        from atoti_jdbc import JdbcLoad

        jdbc_load = JdbcLoad(sql, driver=driver, parameters=parameters, url=url)
        inferred_data_types = self.tables.infer_data_types(jdbc_load)
        types = {**inferred_data_types, **types}
        table = self.create_table(
            table_name,
            data_types=types,
            default_values=default_values,
            keys=keys,
            partitioning=partitioning,
        )
        table.load(jdbc_load)
        return table

    @property
    def ready(self) -> bool:
        """Whether the session is ready or not.

        When ``False``, the server will reject most requests made by users without the :guilabel:`ROLE_ADMIN` role with an HTTP :guilabel:`503 Service Unavailable` status.
        This can be used to prevent queries from being made on a session that has not yet finished its initial setup process (tables and cubes creation, data loading, etc).

        Note:
            This property has no impact in the community edition since the :guilabel:`ROLE_ADMIN` role is always granted.

        Example:
            >>> admin_auth = "admin", "passwd"
            >>> user_auth = "user", "passwd"
            >>> session_config = tt.SessionConfig(
            ...     ready=False, security=tt.SecurityConfig()
            ... )
            >>> session = tt.Session.start(session_config)
            >>> session.ready
            False
            >>> for (username, password), roles in {
            ...     admin_auth: {"ROLE_ADMIN"},
            ...     user_auth: {"ROLE_USER"},
            ... }.items():
            ...     session.security.individual_roles[username] = roles
            ...     session.security.basic_authentication.credentials[username] = (
            ...         password
            ...     )

            The session starts as not ready so only admins can access it:

            .. doctest::
                :hide:

                >>> ping_path = f"{session._client.get_path_and_version_id('activeviam/pivot')[0]}/ping"

            >>> import httpx
            >>> url = f"{session.url}/{ping_path}"
            >>> httpx.get(url, auth=admin_auth).status_code
            200
            >>> httpx.get(url, auth=user_auth).status_code
            503

            Making the session available to all users:

            >>> session.ready = True
            >>> session.ready
            True
            >>> httpx.get(url, auth=admin_auth).status_code
            200
            >>> httpx.get(url, auth=user_auth).status_code
            200

            Making the session unavailable to non-admins again:

            >>> session.ready = False
            >>> session.ready
            False
            >>> httpx.get(url, auth=admin_auth).status_code
            200
            >>> httpx.get(url, auth=user_auth).status_code
            503

            .. doctest::
                :hide:

                >>> del session

        See Also:
            :attr:`atoti.SessionConfig.ready` to configure the initial value of this property.
        """
        return self._client._require_py4j_client().get_readiness()

    @ready.setter
    def ready(self, ready: bool, /) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.set_readiness(ready)
        py4j_client.refresh()

    @deprecated(
        "`Session.start_transaction()` has moved to `Tables.data_transaction()`, replace `session.start_transaction()` with `session.tables.data_transaction()`.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def start_transaction(self) -> AbstractContextManager[None]:
        """Create a data transaction.

        :meta private:
        """
        return self.tables.data_transaction()

    @doc(
        **_TRANSACTION_DOC_KWARGS,
        base_keys_argument="""{"ID"}""",
        base_types_argument="""{"ID": "String", "Quantity": "int"}""",
    )
    def data_model_transaction(
        self,
        *,
        allow_nested: bool = True,
    ) -> AbstractContextManager[None]:
        """Create a data model transaction to batch multiple data model changes.

        Start the transaction with a ``with`` statement.
        The changes will be visible from other clients (e.g. Atoti UI) once the transaction is closed.

        Data model transactions offer "read-your-writes" behavior: changes made inside the transaction are visible to the following statements.

        Note:
            Data model transactions cannot be mixed with data loading operations.

        Warning:
            Data model transactions are work in progress:

            * atomicity and isolation are not guaranteed yet;
            * only measure-related changes are supported for now.

        Args:
            {allow_nested}

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> fact_table = session.create_table(
            ...     "Base",
            ...     data_types={base_types_argument},
            ...     keys={base_keys_argument},
            ... )
            >>> cube = session.create_cube(fact_table)
            >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
            >>> with session.data_model_transaction():
            ...     m["Quantity - 1"] = m["Quantity.SUM"] - 1
            ...
            ...     m["Quantity + 1"] = m["Quantity.SUM"] + 1
            ...     m["Quantity + 1"].description = "Just slightly off"
            ...     m["Quantity + 1"].folder = "Test"
            ...
            ...     m["Quantity + 2"] = m["Quantity + 1"] + 1
            ...     m["Quantity + 2"].formatter = "INT[# ###]"
            >>> fact_table += ("123xyz", 1)
            >>> cube.query(
            ...     m["Quantity.SUM"],
            ...     m["Quantity - 1"],
            ...     m["Quantity + 1"],
            ...     m["Quantity + 2"],
            ... )
              Quantity.SUM Quantity - 1 Quantity + 1 Quantity + 2
            0            1            0            2           3

            With nested transactions allowed:

            >>> def add_foo(cube_name, /, *, session):
            ...     cube = session.cubes[cube_name]
            ...     m = cube.measures
            ...     with session.data_model_transaction():
            ...         m["foo"] = 2_000
            ...         m["foo"].formatter = "INT[# ###]"
            >>> with session.data_model_transaction():
            ...     add_foo(cube.name, session=session)
            ...     m["foo + 1"] = m["foo"] + 1

            With nested transactions not allowed:

            >>> def add_foo_and_query_it(cube_name, /, *, session):
            ...     cube = session.cubes[cube_name]
            ...     m = cube.measures
            ...     with session.data_model_transaction(allow_nested=False):
            ...         m["foo"] = 2_000
            ...         m["foo"].formatter = "INT[# ###]"
            ...     return cube.query(m["foo"])
            >>> add_foo_and_query_it(cube.name, session=session)
                 foo
            0  2000
            >>> with session.data_model_transaction():
            ...     add_foo_and_query_it(cube.name, session=session)
            Traceback (most recent call last):
                ...
            RuntimeError: Cannot start this transaction inside another transaction since nesting is not allowed.

        See Also:
            :meth:`~atoti.tables.Tables.data_transaction`.

        """
        py4j_client = self._client._require_py4j_client()

        def commit() -> None:
            for cube_name in self.cubes:
                py4j_client.publish_measures(cube_name, metada_only=False)

        return transact_data_model(
            allow_nested=allow_nested,
            commit=commit,
            session_id=self._id,
        )

    def create_cube(
        self,
        fact_table: Table,
        name: str | None = None,
        *,
        mode: Literal["auto", "manual", "no_measures"] = "auto",
        filter: CubeFilterCondition | None = None,  # noqa: A002
        id_in_cluster: str | None = None,
        priority: Annotated[int, Field(gt=0)] | None = None,
    ) -> Cube:
        """Create a cube based on the passed table.

        Args:
            fact_table: The table containing the facts of the cube.
            name: The name of the created cube.
                Defaults to the name of *fact_table*.
            mode: The cube creation mode:

                * ``auto``: Creates hierarchies for every key column or non-numeric column of the table, and measures for every numeric column.
                * ``manual``: Does not create any hierarchy or measure (except from the count).
                * ``no_measures``: Creates the hierarchies like ``auto`` but does not create any measures.

                Example:
                    .. doctest::
                        :hide:

                        >>> session = getfixture("default_session")

                    >>> table = session.create_table(
                    ...     "Table",
                    ...     data_types={"id": "String", "value": "double"},
                    ... )
                    >>> cube_auto = session.create_cube(table)
                    >>> sorted(cube_auto.measures)
                    ['contributors.COUNT', 'update.TIMESTAMP', 'value.MEAN', 'value.SUM']
                    >>> list(cube_auto.hierarchies)
                    [('Table', 'id')]
                    >>> cube_no_measures = session.create_cube(
                    ...     table, mode="no_measures"
                    ... )
                    >>> sorted(cube_no_measures.measures)
                    ['contributors.COUNT', 'update.TIMESTAMP']
                    >>> list(cube_no_measures.hierarchies)
                    [('Table', 'id')]
                    >>> cube_manual = session.create_cube(table, mode="manual")
                    >>> sorted(cube_manual.measures)
                    ['contributors.COUNT', 'update.TIMESTAMP']
                    >>> list(cube_manual.hierarchies)
                    []

            filter: If not ``None``, only rows of the database matching this condition will be fed to the cube.
                It can also reduce costs when using DirectQuery since the filter will be applied to the queries executed on the external database to feed the cube.

                Example:
                    >>> df = pd.DataFrame(
                    ...     columns=["Product"],
                    ...     data=[
                    ...         ("phone"),
                    ...         ("watch"),
                    ...         ("laptop"),
                    ...     ],
                    ... )
                    >>> table = session.read_pandas(df, table_name="Filtered table")
                    >>> cube = session.create_cube(table, "Default")
                    >>> cube.query(
                    ...     cube.measures["contributors.COUNT"],
                    ...     levels=[cube.levels["Product"]],
                    ... )
                            contributors.COUNT
                    Product
                    laptop                   1
                    phone                    1
                    watch                    1
                    >>> filtered_cube = session.create_cube(
                    ...     table,
                    ...     "Filtered",
                    ...     filter=table["Product"].isin("watch", "laptop"),
                    ... )
                    >>> filtered_cube.query(
                    ...     filtered_cube.measures["contributors.COUNT"],
                    ...     levels=[filtered_cube.levels["Product"]],
                    ... )
                            contributors.COUNT
                    Product
                    laptop                   1
                    watch                    1

            id_in_cluster: The human-friendly name used to identify this data cube in a cluster.
            priority: The priority of this data cube when using :doc:`distribution </guides/scaling_with_distribution>` with :attr:`atoti.QueryCubeDefinition.allow_data_duplication` set to ``True``.
                Data cubes with the lowest value will be queried in priority.

                * If two data cubes have the same priority, one will be chosen at random.
                * If ``None``, duplicated data is retrieved in priority from the data cube with the fewest members in the :attr:`~atoti.QueryCubeDefinition.distributing_levels`.

        """
        if name is None:
            name = fact_table.name
        definition = CubeDefinition(
            fact_table,
            application_name=...,
            filter=filter,
            hierarchies="auto"
            if (mode == "auto" or mode == "no_measures")
            else "manual",
            id_in_cluster=id_in_cluster,
            measures="auto" if mode == "auto" else "manual",
            priority=priority,
        )
        return self.cubes.set(name, definition)

    def create_scenario(self, name: str, *, origin: str | None = None) -> None:
        """Create a new source scenario.

        Args:
            name: The name of the scenario.
            origin: The scenario to fork.
        """
        py4j_client = self._client._require_py4j_client()
        py4j_client.create_scenario(name, parent_scenario_name=origin)

    def delete_scenario(self, name: str) -> None:
        """Delete the source scenario with the provided name if it exists."""
        py4j_client = self._client._require_py4j_client()
        py4j_client.delete_scenario(name)

    @property
    def scenarios(self) -> AbstractSet[str]:
        """Names of the source scenarios of the session."""
        py4j_client = self._client._require_py4j_client()
        return frozenset(py4j_client.get_scenarios())

    def _warn_if_license_about_to_expire(
        self,
        *,
        minimum_remaining_time: timedelta = _DEFAULT_LICENSE_MINIMUM_REMAINING_TIME,
    ) -> None:
        py4j_client = self._client._require_py4j_client()
        remaining_time = py4j_client.license_end_date - datetime.now()
        if remaining_time < minimum_remaining_time:
            message = f"""The{" embedded " if py4j_client.is_community_license else " "}license key is about to expire, {"update to Atoti's latest version or request an evaluation license key" if py4j_client.is_community_license else "contact ActiveViam to get a new license key"} in the coming {remaining_time.days} days."""
            warn(
                message,
                category=RuntimeWarning,
                stacklevel=2,
            )

    @property
    def widget(self) -> object:
        """Widget to visualize the data in the session interactively.

        Return it from a notebook code cell to display it.
        The widget will appear in the output of this cell and its state will be stored in the metadata of this cell.
        The widget state is automatically updated as the widget is modified through UI interactions.

        Supported notebook environments and their corresponding required dependency:

        * JupyterLab: :mod:`atoti-jupyterlab <atoti_jupyterlab>`.

        Note:
            Some notebook environments provide a cell metadata editor.
            It can be used in the rare situations where the widget state has to be edited manually.

            For instance, in JupyterLab, this editor can be found by opening the :guilabel:`Notebook tools` sidebar and expanding the :guilabel:`Advanced Tools` section.
        """
        return Widget(
            block_until_loaded=self._block_until_widget_loaded,
            get_authentication_headers=lambda: get_authentication_headers(
                self.url, authenticate=self._client._authenticate
            ),
            get_creation_code=self._get_widget_creation_code,
            session_id=self._id,
            session_url=self.url,
        )

    @property
    def url(self) -> str:
        """URL of the session.

        See Also:
            :attr:`~atoti.Session.link`.
        """
        return self._client._url

    @property
    @deprecated(
        "Accessing `Session.port` is deprecated, use `Session.url` instead (and parse it with `urllib.parse.urlparse` if necessary).",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def port(self) -> int:
        """Port on which the session is exposed.

        :meta private:
        """
        parsed_url = urlparse(self.url)
        if parsed_url.port is not None:
            return parsed_url.port
        if parsed_url.scheme == "http":
            return 80
        if parsed_url.scheme == "https":
            return 443
        raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}.")

    @property
    def _basic_credentials(self) -> MutableMapping[UserName, str]:
        return BasicCredentials(client=self._client)

    @property
    def security(self) -> Security:
        return Security(basic_credentials=self._basic_credentials, client=self._client)

    @property
    def proxy(self) -> Proxy:
        return Proxy(client=self._client)

    def wait(self) -> None:
        """Wait for the underlying server subprocess to terminate.

        This will prevent the Python process from exiting.
        """
        return self._server_subprocess.wait()

    @property
    def link(self) -> Link:
        """Link to the session.

        Return it from a notebook code cell to display it.

        * If used inside JupyterLab with :mod:`atoti-jupyterlab <atoti_jupyterlab>` installed, the JupyterLab extension will try to reach the session in this order:

        #. `Jupyter Server Proxy <https://jupyter-server-proxy.readthedocs.io/>`__ if it is enabled.
        #. ``f"{session_protocol}//{jupyter_server_hostname}:{session_port}"``.
        #. :attr:`url`.

        * If used in another environment, :attr:`url` wil be used.

        When :attr:`url` is used and the session is running on another machine, the link may not be reachable.
        In that situation, the session may be reached from ``f"{public_ip_or_domain_of_machine_hosting_session}:{session_port}"``.

        A path can be added to the link with ``/``.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            Linking to an existing dashboard:

            >>> dashboard_id = "92i"
            >>> _ = session.link / "#/dashboard/{dashboard_id}"

        """
        return Link(session_url=self.url)

    def _get_data_types(
        self,
        identifiers: Collection[IdentifierT_co],
        /,
        *,
        cube_name: str,
    ) -> dict[IdentifierT_co, DataType]:
        return self.cubes[cube_name]._get_data_types(identifiers)

    @overload
    def query_mdx(
        self,
        mdx: str,
        /,
        *,
        context: Context = ...,
        explain: Literal[False] = ...,
        keep_totals: bool = ...,
        mode: Literal["pretty"] = ...,
        timeout: Duration = ...,
    ) -> MdxQueryResult: ...

    @overload
    def query_mdx(
        self,
        mdx: str,
        /,
        *,
        context: Context = ...,
        explain: Literal[False] = ...,
        keep_totals: bool = ...,
        mode: Literal["pretty", "raw"] = ...,
        timeout: Duration = ...,
    ) -> pd.DataFrame: ...

    @overload
    def query_mdx(
        self,
        mdx: str,
        /,
        *,
        context: Context = ...,
        explain: Literal[True],
        keep_totals: bool = ...,
        mode: Literal["pretty", "raw"] = ...,
        timeout: Duration = ...,
    ) -> object: ...

    @doc(**_QUERY_KWARGS, keys_argument="""{"Country", "Date"}""")
    def query_mdx(
        self,
        mdx: str,
        /,
        *,
        context: Context = frozendict(),
        explain: bool = False,
        keep_totals: bool = False,
        mode: Literal["pretty", "raw"] = "pretty",
        timeout: Duration = _DEFAULT_QUERY_TIMEOUT,
    ) -> MdxQueryResult | pd.DataFrame | object:
        """Execute an MDX query.

        {widget_conversion}

        Args:
            mdx: The MDX ``SELECT`` query to execute.

                Regardless of the axes on which levels and measures appear in the MDX, the returned DataFrame will have all levels on rows and measures on columns.

                Example:
                    .. doctest::
                        :hide:

                        >>> session = getfixture("default_session")

                    >>> from datetime import date
                    >>> df = pd.DataFrame(
                    ...     columns=["Country", "Date", "Price"],
                    ...     data=[
                    ...         ("China", date(2020, 3, 3), 410.0),
                    ...         ("France", date(2020, 1, 1), 480.0),
                    ...         ("France", date(2020, 2, 2), 500.0),
                    ...         ("France", date(2020, 3, 3), 400.0),
                    ...         ("India", date(2020, 1, 1), 360.0),
                    ...         ("India", date(2020, 2, 2), 400.0),
                    ...         ("UK", date(2020, 2, 2), 960.0),
                    ...     ],
                    ... )
                    >>> table = session.read_pandas(
                    ...     df,
                    ...     keys={keys_argument},
                    ...     table_name="Prices",
                    ... )
                    >>> cube = session.create_cube(table)

                    This MDX:

                    >>> mdx = (
                    ...     "SELECT"
                    ...     "  NON EMPTY Hierarchize("
                    ...     "    DrilldownLevel("
                    ...     "      [Prices].[Country].[ALL].[AllMember]"
                    ...     "    )"
                    ...     "  ) ON ROWS,"
                    ...     "  NON EMPTY Crossjoin("
                    ...     "    [Measures].[Price.SUM],"
                    ...     "    Hierarchize("
                    ...     "      DrilldownLevel("
                    ...     "        [Prices].[Date].[ALL].[AllMember]"
                    ...     "      )"
                    ...     "    )"
                    ...     "  ) ON COLUMNS"
                    ...     "  FROM [Prices]"
                    ... )

                    Returns this DataFrame:

                    >>> session.query_mdx(mdx, keep_totals=True)
                                       Price.SUM
                    Date       Country
                    Total               3,510.00
                    2020-01-01            840.00
                    2020-02-02          1,860.00
                    2020-03-03            810.00
                               China      410.00
                    2020-01-01 China
                    2020-02-02 China
                    2020-03-03 China      410.00
                               France   1,380.00
                    2020-01-01 France     480.00
                    2020-02-02 France     500.00
                    2020-03-03 France     400.00
                               India      760.00
                    2020-01-01 India      360.00
                    2020-02-02 India      400.00
                    2020-03-03 India
                               UK         960.00
                    2020-01-01 UK
                    2020-02-02 UK         960.00
                    2020-03-03 UK

                    But, if it was displayed into a pivot table, would look like this:

                    +---------+-------------------------------------------------+
                    | Country | Price.sum                                       |
                    |         +----------+------------+------------+------------+
                    |         | Total    | 2020-01-01 | 2020-02-02 | 2020-03-03 |
                    +---------+----------+------------+------------+------------+
                    | Total   | 3,510.00 | 840.00     | 1,860.00   | 810.00     |
                    +---------+----------+------------+------------+------------+
                    | China   | 410.00   |            |            | 410.00     |
                    +---------+----------+------------+------------+------------+
                    | France  | 1,380.00 | 480.00     | 500.00     | 400.00     |
                    +---------+----------+------------+------------+------------+
                    | India   | 760.00   | 360.00     | 400.00     |            |
                    +---------+----------+------------+------------+------------+
                    | UK      | 960.00   |            | 960.00     |            |
                    +---------+----------+------------+------------+------------+

            {context}
            {explain}
            keep_totals: Whether the resulting DataFrame should contain, if they are present in the query result, the grand total and subtotals.
                {totals}

            {mode}

              {pretty}

              {raw}

            {timeout}

        See Also:
            :meth:`atoti.Cube.query`

        """
        if explain:
            return explain_query(
                mdx,
                client=self._client,
                context=context,
                timeout=timeout,
            )

        return execute_query(
            mdx,
            client=self._client,
            context=context,
            get_data_types=self._get_data_types,
            get_discovery=lambda: get_discovery(client=self._client),
            get_widget_creation_code=self._get_widget_creation_code,
            keep_totals=keep_totals,
            mode=mode,
            session_id=self._id,
            timeout=timeout,
        )

    def _get_widget_creation_code(self) -> str | None:
        session_variable_name = find_corresponding_top_level_variable_name(self)

        if not session_variable_name:
            return None

        property_name = "widget"
        assert hasattr(self, property_name)
        return f"{session_variable_name}.{property_name}"

    def _block_until_widget_loaded(self, widget_id: str) -> None:
        if self._client._py4j_client is None:
            return

        self._client._py4j_client.block_until_widget_loaded(widget_id)

    def endpoint(
        self,
        route: str,
        *,
        method: HttpMethod = "GET",
    ) -> Callable[[_EndpointCallback], _EndpointCallback]:
        """Create a custom endpoint at ``f"/proxy/{route}"``.

        Note:
            Calling this method overrides :attr:`atoti.Session.proxy`'s :attr:`~atoti.proxy.Proxy.url`.

        The endpoint logic is written in Python but the endpoint is exposed by Atoti Server.
        This allows to deploy the project in a container or a VM with a single opened port (the one of Atoti Server) instead of two.

        The decorated function must:

        * take three parameters with respective types:

          * :class:`atoti.endpoint.Request`
          * :class:`atoti.User`
          * :class:`atoti.Session`

        * return a response body as JSON convertible data

        Args:
            route: The template of the path after ``"/proxy"``.
                For instance, if ``"foo/bar"`` is passed, a request to ``"/proxy/foo/bar?query=string`` will match.
                Path parameters can be configured by wrapping their name in curly braces in the template.
            method: The HTTP method the request must be using to trigger this endpoint.
                ``DELETE``, ``PATCH``, ``POST``, and ``PUT`` requests can have a body but it must be JSON.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> import httpx
            >>> df = pd.DataFrame(
            ...     columns=["Year", "Month", "Day", "Quantity"],
            ...     data=[
            ...         (2019, 7, 1, 15),
            ...         (2019, 7, 2, 20),
            ...     ],
            ... )
            >>> table = session.read_pandas(
            ...     df, keys={"Year", "Month", "Day"}, table_name="Quantity"
            ... )

            >>> @session.endpoint("tables/{table_name}/count", method="GET")
            ... def get_table_row_count(request, user, session, /):
            ...     table_name = request.path_parameters["table_name"]
            ...     return session.tables[table_name].row_count
            >>> response = httpx.get(f"{session.url}/proxy/tables/{table.name}/count")
            >>> response.raise_for_status().json()
            2

            >>> @session.endpoint("tables/{table_name}/rows", method="POST")
            ... def append_rows_to_table(request, user, session, /):
            ...     rows = request.body
            ...     table_name = request.path_parameters["table_name"]
            ...     table = session.tables[table_name]
            ...     dataframe = pd.DataFrame(rows, columns=list(table))
            ...     table.load(dataframe)
            >>> response = httpx.post(
            ...     f"{session.url}/proxy/tables/{table.name}/rows",
            ...     json=[
            ...         (2021, 5, 19, 50),
            ...         (2021, 5, 20, 6),
            ...     ],
            ... )
            >>> response.status_code
            200
            >>> response = httpx.get(f"{session.url}/proxy/tables/{table.name}/count")
            >>> response.raise_for_status().json()
            4
            >>> table.head()
                            Quantity
            Year Month Day
            2019 7     1          15
                       2          20
            2021 5     19         50
                       20          6

        See Also:
            :attr:`atoti.Session.proxy`.

        """
        if route[0] == "/" or "?" in route or "#" in route:
            raise ValueError(
                f"Invalid route '{route}'. It should not start with '/' and not contain '?' or '#'.",
            )

        def endpoint_decorator(callback: _EndpointCallback, /) -> _EndpointCallback:
            if self._endpoint_server.start():
                self.proxy.url = self._endpoint_server.url

            def _callback(request: Request, user: User) -> JsonValue:
                return callback(request, user, self)

            self._endpoint_server.register_endpoint(
                http_method=method,
                path=route,
                callback=_callback,
            )
            return callback

        return endpoint_decorator

    def export_translations_template(self, path: Path) -> None:
        """Export a template containing all translatable values in the session's cubes.

        Args:
            path: The path at which to write the template.
        """
        py4j_client = self._client._require_py4j_client()
        py4j_client.export_i18n_template(path)

    def _create_memory_analysis_report(self, directory: Path, /) -> None:
        """Create a memory analysis report.

        Args:
            directory: The path of the directory where the report will be created.
              Its parent directory must already exist.
        """
        assert directory.parent.is_dir()
        py4j_client = self._client._require_py4j_client()
        py4j_client.memory_analysis_export(directory.parent, directory.name)

    def _reset(self) -> None:
        self._endpoint_server.stop()

        py4j_client = self._client._py4j_client
        if py4j_client is not None:
            py4j_client.reset()

            if not py4j_client.is_community_license and py4j_client.is_secured:
                self._basic_credentials.clear()

                if self._client._content_client is not None:
                    with suppress(httpx.HTTPStatusError):
                        self._client._content_client.delete(_SECURITY_ROOT_DIRECTORY)

    @property
    def user(self) -> User:
        """The user behind this session.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            A session without security configured has a single user, who is both anonymous and an administrator:

            >>> user = session.user
            >>> user.name
            'anonymousUser'
            >>> sorted(user.roles)
            ['ROLE_ADMIN', 'ROLE_ANONYMOUS', 'ROLE_USER']

            The user that :meth:`started <atoti.Session.start>` a secured session has the same characteristics:

            >>> session_config = tt.SessionConfig(security=tt.SecurityConfig())
            >>> secured_session = tt.Session.start(session_config)
            >>> root = secured_session.user
            >>> root.name
            'anonymousUser'
            >>> sorted(root.roles)
            ['ROLE_ADMIN', 'ROLE_ANONYMOUS', 'ROLE_USER']

            Adding a new user:

            >>> username, password = "Cooper", "abcdef123456"
            >>> secured_session.security.individual_roles[username] = {
            ...     "ROLE_PILOT",
            ...     "ROLE_USER",
            ... }
            >>> secured_session.security.basic_authentication.credentials[username] = (
            ...     password
            ... )

            Connecting as this new user:

            >>> cooper_session = tt.Session.connect(
            ...     secured_session.url,
            ...     authentication=tt.BasicAuthentication(username, password),
            ... )
            >>> cooper = cooper_session.user
            >>> cooper.name
            'Cooper'
            >>> sorted(cooper.roles)
            ['ROLE_PILOT', 'ROLE_USER']

            .. doctest::
                :hide:

                >>> del cooper_session
                >>> del secured_session

        """
        output = self._client._require_graphql_client().get_current_user()
        return User(name=output.current_user.name, roles=set(output.current_user.roles))
