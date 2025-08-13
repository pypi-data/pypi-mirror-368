from __future__ import annotations

import json
import re
from collections.abc import (
    Callable,
    Collection,
    Generator,
    Mapping,
    Sequence,
    Set as AbstractSet,
)
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from types import FunctionType
from typing import Any, Final, Literal, TypeAlias, Union, cast, final

from py4j.clientserver import ClientServer, JavaParameters, PythonParameters
from py4j.java_collections import JavaMap
from py4j.java_gateway import DEFAULT_ADDRESS, DEFAULT_PORT, JavaGateway, JavaObject
from pydantic import JsonValue, TypeAdapter, ValidationError

# Remove this once the session config serialization logic on the Java side is synchronized with the Python side.
from pydantic_core import to_json  # pylint: disable=undeclared-dependency

from .._constant import Constant, Scalar
from .._constant_column_condition import (
    ConstantColumnCondition,
    ConstantColumnLeafCondition,
)
from .._cube_filter_condition import CubeFilterCondition
from .._cube_mask_condition import CubeMaskCondition
from .._data_type import DataType, parse_data_type
from .._identification import (
    ApplicationName,
    ClusterIdentifier,
    ColumnIdentifier,
    ExternalColumnIdentifier,
    ExternalTableIdentifier,
    HierarchyIdentifier,
    Identifiable,
    IdentifierT_co,
    LevelIdentifier,
    MeasureIdentifier,
    QueryCubeIdentifier,
    TableIdentifier,
    identify,
)
from .._operation import (
    HierarchyMembershipCondition,
    LogicalCondition,
    MembershipCondition,
    RelationalCondition,
    RelationalOperator,
    condition_from_dnf,
    dnf_from_condition,
)
from .._pydantic import get_type_adapter
from .._report import LoadingReport, _warn_new_errors
from .._session_id import SessionId
from .._table_drop_filter_condition import TableDropFilterCondition
from .._transaction import (
    DataTransactionTableIdentifiers,
    get_data_model_transaction_id,
    get_data_transaction_id,
    transact_data,
)
from ..aggregate_provider import AggregateProvider
from ..cluster_definition import ClusterDefinition
from ..data_load import DataLoad
from ..data_load.csv_load import _PLUGIN_KEY as _CSV_LOAD_PLUGIN_KEY
from ..data_stream import DataStream
from ..directquery import ExternalAggregateTable
from ..directquery._external_aggregate_table._external_aggregate_table_sql import (
    ExternalAggregateTableSql,
)
from ..directquery._external_aggregate_table._external_measure import ExternalMeasure
from ..directquery._external_table_config import EmulatedTimeTravelTableConfig
from ..directquery._external_table_update import (
    ExternalTableUpdate,
    _ExternalTableUpdateChangeType,
    _ExternalTableUpdatePerimeterCondition,
)
from ..distribution_protocols import DiscoveryProtocol
from ..distribution_protocols._custom_discovery_protocol import CustomDiscoveryProtocol
from ..order import CustomOrder, NaturalOrder
from ..order._order import Order
from ._retrieve_stack_trace_before_it_is_too_late import (
    retrieve_stack_trace_before_it_is_too_late,
)
from ._utils import (
    to_java_list,
    to_java_map,
    to_java_object,
    to_java_object_array,
    to_java_set,
    to_java_string_array,
    to_python_dict,
    to_python_list,
    to_python_set,
    to_store_field,
)

_JavaExternalTableChangeType = Literal[
    "ADD_ROWS",
    "UPDATE_ROWS",
    "REMOVE_ROWS",
    "MIXED_CHANGES",
]
_EXTERNAL_TABLE_UPDATE_CHANGE_TYPE_TO_JAVA_CHANGE_TYPE: dict[
    _ExternalTableUpdateChangeType,
    _JavaExternalTableChangeType,
] = {
    "add": "ADD_ROWS",
    "update": "UPDATE_ROWS",
    "remove": "REMOVE_ROWS",
    "mixed": "MIXED_CHANGES",
}


def _parse_measure_data_type(value: str, /) -> DataType:
    parts = value.split("nullable ")
    return parse_data_type(parts[-1])


def _to_data_type(java_type: Any, /) -> DataType:
    return parse_data_type(java_type.getJavaType())


def _convert_store_field_to_column_identifier(store_field: Any, /) -> ColumnIdentifier:
    return ColumnIdentifier(
        TableIdentifier(store_field.getStore()),
        store_field.getName(),
    )


def _convert_java_column_types(schema: Any, /) -> dict[str, DataType]:
    field_names = list(schema.fieldNames())
    field_types = list(schema.types())
    return {
        field_names[i]: _to_data_type(field_types[i]) for i in range(len(field_names))
    }


def _convert_java_emulated_time_travel_table(
    config: Any, /
) -> EmulatedTimeTravelTableConfig | None:
    if not config:
        return None
    return EmulatedTimeTravelTableConfig(
        valid_from_column_name=config.fromColumnExternalName(),
        valid_to_column_name=config.toColumnExternalName(),
    )


_ConstantMembershipCondition: TypeAlias = MembershipCondition[
    IdentifierT_co, Literal["in"], Constant
]
_ConstantMembershipCondition.__parameters__ = (IdentifierT_co,)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
_ConstantRelationalCondition: TypeAlias = RelationalCondition[
    IdentifierT_co, Literal["=="], Constant
]
_ConstantRelationalCondition.__parameters__ = (IdentifierT_co,)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
_ConstantLeafCondition: TypeAlias = Union[  # noqa: UP007
    _ConstantMembershipCondition[IdentifierT_co],
    _ConstantRelationalCondition[IdentifierT_co],
]
_ConstantLeafCondition.__parameters__ = (IdentifierT_co,)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
_ConstantLogicalCondition: TypeAlias = LogicalCondition[
    _ConstantLeafCondition[IdentifierT_co], Literal["&"]
]
_ConstantLogicalCondition.__parameters__ = (IdentifierT_co,)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
_ConstantCondition: TypeAlias = Union[  # noqa: UP007
    _ConstantLeafCondition[IdentifierT_co], _ConstantLogicalCondition[IdentifierT_co]
]
_ConstantCondition.__parameters__ = (IdentifierT_co,)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]


def _constant_condition_from_java_mapping(
    mapping: Mapping[str, Any],
    /,
    *,
    identify: Callable[[str], IdentifierT_co],
) -> (
    _ConstantLeafCondition[IdentifierT_co]
    | LogicalCondition[_ConstantLeafCondition[IdentifierT_co], Literal["&"]]
    | None
):
    if not mapping:
        return None

    return condition_from_dnf(
        (
            [
                MembershipCondition.of(
                    subject=identify(key),
                    operator="in",
                    elements=to_python_set(elements),
                )
                for key, elements in mapping.items()
            ],
        ),
    )


_REALTIME_SOURCE_KEYS = ["KAFKA"]


@final
class _Metaclass(type):
    """Meta class for ``Py4jClient`` that makes all methods eagerly evaluate error messages of uncaught ``Py4JJavaError``s."""

    def __new__(  # pylint: disable=too-many-positional-parameters
        cls, classname: str, bases: tuple[type, ...], class_dict: Mapping[str, Any]
    ) -> _Metaclass:
        new_class_dict = {
            attribute_name: retrieve_stack_trace_before_it_is_too_late(attribute)
            if isinstance(attribute, FunctionType)
            else attribute
            for attribute_name, attribute in class_dict.items()
        }
        return type.__new__(cls, classname, bases, new_class_dict)


@final
class Py4jClient(metaclass=_Metaclass):
    @contextmanager
    @staticmethod
    def create(
        *,
        address: str | None,
        detached: bool,
        distributed: bool,
        py4j_auth_token: str | None,
        py4j_java_port: int | None,
        session_id: SessionId,
    ) -> Generator[Py4jClient, None, None]:
        if address is None:
            address = DEFAULT_ADDRESS

        if py4j_java_port is None:
            py4j_java_port = DEFAULT_PORT

        # Connect to the Java side using the provided Java port and start the Python callback server with a dynamic port.
        gateway = ClientServer(
            java_parameters=JavaParameters(
                address=address,
                auth_token=py4j_auth_token,
                port=py4j_java_port,
            ),
            python_parameters=PythonParameters(daemonize=True, port=0),
        )

        try:
            # Retrieve the port on which the python callback server was bound to.
            cb_server = gateway.get_callback_server()
            assert cb_server
            python_port = cb_server.get_listening_port()

            # Tell the Java side to connect to the Python callback server with the new Python port.
            gateway_server = gateway.java_gateway_server
            assert gateway_server is not None
            gateway_server.resetCallbackClient(  # pyright: ignore[reportCallIssue, reportOptionalCall]
                gateway_server.getCallbackClient().getAddress(),  # pyright: ignore[reportCallIssue, reportOptionalCall]
                python_port,
            )

            yield Py4jClient(
                distributed=distributed,
                gateway=gateway,
                session_id=session_id,
            )
        finally:
            if not detached:
                gateway.shutdown()

    def __init__(
        self,
        *,
        distributed: bool,
        gateway: JavaGateway,
        session_id: SessionId,
    ):
        self.gateway: Final = gateway
        self._distributed: Final = distributed
        self._session_id: Final = session_id

    @property
    def jvm(self) -> Any:
        return self.gateway.jvm

    @property
    def py4j_client(self) -> Any:
        return self.java_session.api()

    @property
    def java_session(self) -> Any:
        return self.gateway.entry_point

    def refresh(self) -> None:
        if get_data_model_transaction_id(self._session_id) is not None:
            raise NotImplementedError(
                "This operation is not supported inside data model transactions yet.",
            )

        self.py4j_client.refresh()

        if not self._distributed:
            _warn_new_errors(self.get_new_load_errors())

    def _get_java_external_table_update_condition(
        self,
        perimeter: _ExternalTableUpdatePerimeterCondition | None,
        /,
    ) -> JavaObject:
        if perimeter is None:
            return self.jvm.com.activeviam.directquery.application.api.refresh.condition.ConditionFactory.allRows()

        dnf = dnf_from_condition(perimeter)

        or_conditions: list[JavaObject] = []

        for conjunct_conditions in dnf:
            and_conditions: list[JavaObject] = []

            for leaf_condition in conjunct_conditions:
                match leaf_condition:
                    case MembershipCondition(
                        subject=subject,
                        operator="in",  # `IS_NOT_IN` is not supported.
                        elements=elements,
                    ):
                        java_condition = getattr(
                            self.jvm.com.activeviam.directquery.application.api.refresh.condition.ConditionFactory,
                            "in",
                        )(
                            to_java_object(
                                subject.column_name,  # type: ignore[attr-defined]
                                gateway=self.gateway,
                            ),
                            to_java_set(elements, gateway=self.gateway),
                        )
                    case RelationalCondition(
                        subject=subject, operator=operator, target=target
                    ):
                        java_condition = self.jvm.com.activeviam.directquery.application.api.refresh.condition.ConditionFactory.equal(
                            subject.column_name,  # type: ignore[union-attr]
                            to_java_object(target, gateway=self.gateway),
                        )
                        match operator:
                            case "==":
                                ...
                            case "!=":
                                java_condition = getattr(
                                    self.jvm.com.activeviam.directquery.application.api.refresh.condition.ConditionFactory,
                                    "not",
                                )(java_condition)

                and_conditions.append(java_condition)

            or_conditions.append(
                getattr(
                    self.jvm.com.activeviam.directquery.application.api.refresh.condition.ConditionFactory,
                    "and",
                )(to_java_list(and_conditions, gateway=self.gateway)),
            )

        return getattr(
            self.jvm.com.activeviam.directquery.application.api.refresh.condition.ConditionFactory,
            "or",
        )(to_java_list(or_conditions, gateway=self.gateway))

    def _get_java_external_table_update(
        self,
        table_update: ExternalTableUpdate,
        /,
    ) -> JavaObject:
        table_name = identify(table_update.table).table_name
        if table_update.change_type == "infer":
            java_change_type: _JavaExternalTableChangeType = "ADD_ROWS"
            return self.jvm.com.activeviam.directquery.application.api.refresh.TableUpdateDetail.create(
                table_name,
                self.jvm.com.activeviam.directquery.application.api.refresh.ChangeType.valueOf(
                    java_change_type,
                ),
                self.jvm.com.activeviam.directquery.application.api.refresh.condition.ConditionFactory.unknown(),
            )

        return self.jvm.com.activeviam.directquery.application.api.refresh.TableUpdateDetail.create(
            table_name,
            self.jvm.com.activeviam.directquery.application.api.refresh.ChangeType.valueOf(
                _EXTERNAL_TABLE_UPDATE_CHANGE_TYPE_TO_JAVA_CHANGE_TYPE[
                    table_update.change_type
                ],
            ),
            self._get_java_external_table_update_condition(table_update.perimeter),
        )

    def _get_change_description(self, *updates: ExternalTableUpdate) -> JavaObject:
        java_table_updates = [
            self._get_java_external_table_update(update) for update in updates
        ]
        return self.jvm.com.activeviam.directquery.application.api.refresh.ChangeDescription.create(
            to_java_list(java_table_updates, gateway=self.gateway),
        )

    def incremental_refresh(self, *updates: ExternalTableUpdate) -> None:
        change_description = self._get_change_description(*updates)
        self.py4j_client.refresh(change_description)

    @property
    def license_end_date(self) -> datetime:
        return datetime.fromtimestamp(self.java_session.getLicenseEndDate() / 1000)

    @property
    def is_community_license(self) -> bool:
        return cast(bool, self.java_session.isCommunityLicense())

    @property
    def is_secured(self) -> bool:
        return (
            self.java_session.enterpriseSession().getConfiguredSecurityProvider()
            is not None
        )

    def publish_measures(
        self, cube_name: str, /, *, metada_only: bool | None = None
    ) -> None:
        if metada_only is None:
            metada_only = get_data_model_transaction_id(self._session_id) is not None
        self._outside_transaction_api().publishMeasures(cube_name, metada_only)

    def reset(self) -> None:
        self.py4j_client.clearSession()

    def get_readiness(self) -> bool:
        ready = self.py4j_client.isReady()
        assert isinstance(ready, bool)
        return ready

    def set_readiness(self, ready: bool, /) -> None:  # noqa: FBT001
        self.py4j_client.setReadiness(ready)

    def generate_jwt(self) -> str:
        """Return the JWT required to authenticate against this session."""
        return cast(str, self.java_session.generateJwt())

    def set_locale(self, locale: str, /) -> None:
        """Set the locale to use for the session."""
        self._enterprise_api().setLocale(locale)

    def export_i18n_template(self, path: Path, /) -> None:
        """Generate a template translations file at the desired location."""
        self._enterprise_api().exportI18nTemplate(str(path))

    def _outside_transaction_api(self) -> Any:
        return self.py4j_client.outsideTransactionApi(
            get_data_transaction_id(self._session_id) is not None
        )

    def _enterprise_api(self) -> Any:
        return self.py4j_client.enterpriseApi(
            get_data_transaction_id(self._session_id) is not None
        )

    def _convert_load_options(self, options: Mapping[str, object], /) -> JavaMap:
        java_options = {}
        for option in options:
            value = options[option]
            if isinstance(value, Mapping):
                value = to_java_map(value, gateway=self.gateway)
            elif isinstance(value, Collection) and not isinstance(value, str):
                value = to_java_list(value, gateway=self.gateway)
            java_options[option] = value
        return to_java_map(java_options, gateway=self.gateway)

    def infer_data_types(self, data: DataLoad, /) -> dict[str, DataType]:
        keys: Sequence[str] = []
        default_values: Mapping[str, DataType] = {}
        java_options = self._convert_load_options(data._options)
        java_data_types = to_python_dict(
            self._outside_transaction_api()
            .discoverCsvFileFormat(
                to_java_list(keys, gateway=self.gateway),
                to_java_map(default_values, gateway=self.gateway),
                java_options,
            )
            .getTypes()
            if data._plugin_key == _CSV_LOAD_PLUGIN_KEY
            else self._outside_transaction_api().inferTypesFromDataSource(
                data._plugin_key,
                to_java_list(keys, gateway=self.gateway),
                to_java_map(default_values, gateway=self.gateway),
                java_options,
            ),
        )
        return {
            column_name: _to_data_type(java_data_type)
            for column_name, java_data_type in java_data_types.items()
        }

    def load_data_into_table(
        self,
        data: DataLoad | DataStream,
        /,
        *,
        scenario_name: str | None,
        table_identifier: TableIdentifier,
    ) -> None:
        java_options = self._convert_load_options(data._options)
        self.py4j_client.loadDataSourceIntoStore(
            table_identifier.table_name,
            data._plugin_key,
            self.jvm.io.atoti.runtime.internal.loading.impl.LoadingParams().setBranch(
                scenario_name,
            ),
            java_options,
            get_data_transaction_id(self._session_id),
        )
        _warn_new_errors(self.get_new_load_errors())

    def create_scenario(
        self,
        scenario_name: str,
        /,
        *,
        parent_scenario_name: str | None,
    ) -> None:
        self._outside_transaction_api().createBranch(
            scenario_name,
            parent_scenario_name,
        )

    def get_scenarios(self) -> set[str]:
        return to_python_set(self.py4j_client.getBranches())

    def delete_scenario(self, scenario: str, /) -> None:
        if self._outside_transaction_api().deleteBranch(scenario).isEmpty():
            raise ValueError("Cannot delete the default scenario")

    def start_data_transaction(
        self,
        *,
        initiated_by_user: bool,
        scenario_name: str | None,
        table_identifiers: DataTransactionTableIdentifiers | None,
    ) -> str:
        return str(
            self.py4j_client.startTransaction(
                scenario_name,
                initiated_by_user,
                to_java_set(
                    {
                        identifier.table_name
                        for identifier in table_identifiers or set()
                    },
                    gateway=self.gateway,
                ),
            )
        )

    def end_data_transaction(
        self,
        transaction_id: str,
        /,
        *,
        has_succeeded: bool,
    ) -> None:
        self.py4j_client.endTransaction(
            has_succeeded,
            transaction_id,
        )

    def _java_map_from_constant_condition(
        self,
        condition: _ConstantCondition[IdentifierT_co] | None,
        /,
        *,
        get_key: Callable[[IdentifierT_co], object],
    ) -> JavaMap:
        result: dict[IdentifierT_co, AbstractSet[Constant]] = {}

        match condition:
            case None:
                ...
            case _:
                dnf: tuple[tuple[_ConstantLeafCondition[IdentifierT_co], ...]] = (
                    dnf_from_condition(
                        condition,
                    )
                )
                (conjunct_conditions,) = dnf

                for leaf_condition in conjunct_conditions:
                    match leaf_condition:
                        case MembershipCondition(
                            subject=subject, operator="in", elements=elements
                        ):
                            result[subject] = elements
                        case RelationalCondition(
                            subject=subject, operator="==", target=target
                        ):
                            result[subject] = {target}

        return to_java_map(
            {
                get_key(identifier): to_java_list(
                    [
                        to_java_object(constant, gateway=self.gateway)
                        for constant in constants
                    ],
                    gateway=self.gateway,
                )
                for identifier, constants in result.items()
            },
            gateway=self.gateway,
        )

    def _convert_python_aggregate_provider_to_java(
        self,
        aggregate_provider: AggregateProvider,
        /,
    ) -> JavaObject:
        java_levels = to_java_list(
            [identify(level)._java_description for level in aggregate_provider.levels]
            if aggregate_provider.levels
            else [],
            gateway=self.gateway,
        )

        java_measures = (
            None
            if aggregate_provider.measures is None
            else to_java_list(
                [
                    identify(measure).measure_name
                    for measure in aggregate_provider.measures
                ],
                gateway=self.gateway,
            )
        )

        java_filters = self._java_map_from_constant_condition(
            aggregate_provider.filter,
            get_key=lambda identifier: identifier._java_description,
        )

        return (
            self.jvm.io.atoti.runtime.internal.impl.AggregateProviderDescription.builder()
            .pluginKey(aggregate_provider.key.upper())
            .levelDescriptions(java_levels)
            .measures(java_measures)
            .partitioning(aggregate_provider.partitioning)
            .filters(java_filters)
            .build()
        )

    def _create_java_cluster_config(
        self,
        *,
        allowed_application_names: AbstractSet[str] | None,
        cube_url: str | None,
        cube_port: int | None,
        discovery_protocol: DiscoveryProtocol | None,
        auth_token: str,
    ) -> Any:
        builder = self.jvm.io.atoti.runtime.internal.DistributedApi.DiscoveryConfig.builder().authToken(
            auth_token
        )

        # Only calling the builder's methods with non `None` values to not override its defaults.
        if allowed_application_names is not None:
            builder = builder.allowedApplicationNames(
                to_java_list(allowed_application_names, gateway=self.gateway),
            )
        if cube_url is not None:
            builder = builder.cubeUrl(cube_url)
        if cube_port is not None:
            builder = builder.cubePort(cube_port)
        if discovery_protocol is not None:
            builder = builder.discoveryProtocolXml(discovery_protocol._xml)

        return builder.build()

    def auto_join_distributed_clusters(self, *, cube_name: str) -> None:
        if not self.is_community_license:
            self._enterprise_api().autoJoinDistributedClusters(cube_name)

    def auto_join_new_distributed_clusters(
        self, *, cluster_names: Collection[str]
    ) -> None:
        if not self.is_community_license:
            self._enterprise_api().autoJoinNewDistributedClusters(
                to_java_list(cluster_names, gateway=self.gateway)
            )

    def join_distributed_cluster(
        self,
        *,
        cluster_name: str,
        data_cube_name: str,
    ) -> None:
        self._enterprise_api().addDataCubeToDistributedCluster(
            data_cube_name,
            cluster_name,
        )

    def remove_from_distributed_cluster(self, *, data_cube_name: str) -> None:
        self._enterprise_api().removeDataCubeFromDistributedCluster(data_cube_name)

    def create_distributed_cluster(
        self, *, cluster_name: str, cluster_config: ClusterDefinition
    ) -> None:
        java_cluster_config = self._create_java_cluster_config(
            allowed_application_names=cluster_config.application_names,
            cube_url=cluster_config.cube_url,
            cube_port=cluster_config.cube_port,
            discovery_protocol=cluster_config.discovery_protocol,
            auth_token=cluster_config.authentication_token,
        )

        self._enterprise_api().createDistributedCluster(
            cluster_name,
            java_cluster_config,
        )

    def get_clusters(self) -> list[ClusterIdentifier]:
        clusters = self._enterprise_api().getDistributedClusters()
        return [
            ClusterIdentifier(cluster_name) for cluster_name in to_python_dict(clusters)
        ]

    def get_cluster_application_names(
        self, cluster_identifier: ClusterIdentifier, /
    ) -> set[ApplicationName]:
        cluster = self._enterprise_api().getDistributedCluster(
            cluster_identifier.cluster_name
        )
        assert cluster is not None
        return to_python_set(cluster.getAllowedApplicationNames())

    def get_cluster_discovery_protocol(
        self, cluster_identifier: ClusterIdentifier, /
    ) -> DiscoveryProtocol | None:
        cluster = self._enterprise_api().getDistributedCluster(
            cluster_identifier.cluster_name
        )
        assert cluster is not None

        discovery_protocol_xml = cluster.getDiscoveryProtocolXml()

        if discovery_protocol_xml is None:
            return None

        match = re.match(r"<\s*(?P<root_tag_name>[^\s/>]+)", discovery_protocol_xml)
        if match is None:
            raise ValueError(f"Could not find root tag in `{discovery_protocol_xml}`")
        name = match.group("root_tag_name")

        return CustomDiscoveryProtocol(
            name=name,
            xml=discovery_protocol_xml,
        )

    def delete_cluster(self, cluster_identifier: ClusterIdentifier, /) -> None:
        self._enterprise_api().deleteDistributedCluster(cluster_identifier.cluster_name)

    def get_table_partitioning(self, identifier: TableIdentifier, /) -> str:
        """Return the table's partitioning."""
        return cast(
            str,
            self._outside_transaction_api().getStorePartitioning(identifier.table_name),
        )

    def get_column_data_type(self, identifier: ColumnIdentifier, /) -> DataType:
        return _to_data_type(
            self.py4j_client.getFieldType(
                identifier.column_name,
                identifier.table_identifier.table_name,
            ),
        )

    @staticmethod
    def _convert_reports(reports: Collection[Any]) -> list[LoadingReport]:
        """Convert the Java report to Python ones."""
        return [
            LoadingReport(
                name=r.getName(),
                source=r.getType(),
                loaded=r.getLoadedCount(),
                errors=r.getErrorCount(),
                duration=r.getDuration(),
                error_messages=to_python_list(r.getFailureMessages()),
            )
            for r in reports
        ]

    def clear_loading_report(self, identifier: TableIdentifier, /) -> None:
        self.py4j_client.clearLoadingReports(identifier.table_name)

    def get_loading_report(self, identifier: TableIdentifier, /) -> list[LoadingReport]:
        return self._convert_reports(
            to_python_list(self.py4j_client.getLoadingReports(identifier.table_name)),
        )

    def get_new_load_errors(self) -> dict[str, int]:
        """Return the new loading errors per table."""
        errors = self.py4j_client.getNewLoadingErrors()
        return to_python_dict(errors)

    def get_selection_fields(self, cube_name: str, /) -> list[ColumnIdentifier]:
        """Return the list of fields that are part of the cube's datastore selection."""
        java_fields = self._outside_transaction_api().getSelectionFields(cube_name)
        return [
            ColumnIdentifier(
                TableIdentifier(java_field.getStore()),
                java_field.getName(),
            )
            for java_field in to_python_list(java_fields)
        ]

    def create_cube_from_table(
        self,
        cube_name: str,
        /,
        *,
        catalog_names: AbstractSet[str],
        application_name: str | None,
        table_identifier: TableIdentifier,
        mode: str,
        filter: CubeFilterCondition | None = None,  # noqa: A002
        id_in_cluster: str | None,
        priority: int | None,
    ) -> None:
        java_column_conditions = (
            None
            if filter is None
            else self._convert_python_condition_to_java_column_conditions(filter)
        )

        self._outside_transaction_api().createCubeFromStore(
            table_identifier.table_name,
            cube_name,
            to_java_list(catalog_names, gateway=self.gateway),
            application_name,
            mode,
            java_column_conditions,
            id_in_cluster,
            priority,
        )

    def create_query_cube(
        self,
        cube_name: str,
        *,
        application_names: Collection[str],
        catalog_names: Collection[str],
        cluster_name: str,
        distribution_levels: Collection[str],
        allow_data_duplication: bool,
    ) -> None:
        self.py4j_client.createDistributedCube(
            cube_name,
            to_java_list(catalog_names, gateway=self.gateway),
            cluster_name,
            to_java_list(application_names, gateway=self.gateway),
            to_java_list(distribution_levels, gateway=self.gateway),
            allow_data_duplication,
        )

    def get_distributing_levels(
        self, query_cube_identifier: QueryCubeIdentifier, /
    ) -> set[str]:
        return to_python_set(
            self.py4j_client.getDistributionLevels(query_cube_identifier.cube_name)
        )

    def delete_cube(self, cube_name: str, /) -> None:
        if not self._outside_transaction_api().deleteCube(cube_name):
            raise KeyError(cube_name)

    def get_cube_application_name(self, cube_name: str, /) -> str:
        return cast(str, self._outside_transaction_api().getApplicationName(cube_name))

    def set_cube_application_name(
        self, cube_name: str, application_name: str, /
    ) -> None:
        self._outside_transaction_api().setApplicationName(cube_name, application_name)

    def get_table_size(
        self,
        identifier: TableIdentifier,
        /,
        *,
        scenario_name: str | None,
    ) -> int:
        """Get the size of the table on its current scenario."""
        return cast(
            int,
            self._outside_transaction_api().getStoreSize(
                identifier.table_name,
                scenario_name,
            ),
        )

    def _build_java_column_condition(
        self,
        condition: ConstantColumnLeafCondition,
        /,
    ) -> JavaObject:
        column_data_type = self.get_column_data_type(condition.subject)

        ColumnCondition = self.jvm.io.atoti.runtime.internal.condition.ColumnCondition  # noqa: N806
        comparison_operator_from_relational_operator: Mapping[
            RelationalOperator,
            Any,
        ] = {
            "==": ColumnCondition.ComparisonOperator.EQ,
            "!=": ColumnCondition.ComparisonOperator.NE,
            "<": ColumnCondition.ComparisonOperator.LT,
            "<=": ColumnCondition.ComparisonOperator.LE,
            ">": ColumnCondition.ComparisonOperator.GT,
            ">=": ColumnCondition.ComparisonOperator.GE,
        }

        nullable: Final = True

        return (
            ColumnCondition.builder()
            .storeField(to_store_field(condition.subject, gateway=self.gateway))
            .value(
                to_java_object(
                    condition.target,
                    data_type=column_data_type,
                    gateway=self.gateway,
                )
                if isinstance(condition, RelationalCondition)
                else to_java_object_array(
                    [
                        to_java_object(
                            element,
                            gateway=self.gateway,
                            data_type=column_data_type,
                        )
                        for element in condition.elements
                    ],
                    gateway=self.gateway,
                ),
            )
            .comparisonOperator(
                comparison_operator_from_relational_operator[condition.operator]
                if isinstance(condition, RelationalCondition)
                else ColumnCondition.ComparisonOperator.ISIN,
            )
            .fieldType(
                self.jvm.io.atoti.runtime.internal.loading.impl.TypeImpl(
                    column_data_type,
                    nullable,
                ),
            )
            .build()
        )

    def delete_rows_from_table(
        self,
        identifier: TableIdentifier,
        /,
        *,
        scenario_name: str | None,
        condition: TableDropFilterCondition | None = None,
    ) -> None:
        java_column_conditions = (
            None
            if condition is None
            else self._convert_python_condition_to_java_column_conditions(condition)
        )

        def delete_on_store_branch() -> None:
            transaction_id = get_data_transaction_id(self._session_id)
            assert transaction_id is not None
            self.py4j_client.deleteOnStoreBranch(
                identifier.table_name,
                scenario_name,
                java_column_conditions,
                transaction_id,
            )

        self._inside_transaction(
            delete_on_store_branch,
            scenario_name=scenario_name,
        )

    def update_hierarchies_for_cube(
        self,
        cube_name: str,
        *,
        deleted: Mapping[str, Collection[str]],
        updated: Mapping[str, Mapping[str, Mapping[str, ColumnIdentifier]]],
    ) -> None:
        java_deleted = to_java_map(
            {
                dimension_name: to_java_list(hierarchy_names, gateway=self.gateway)
                for dimension_name, hierarchy_names in deleted.items()
            },
            gateway=self.gateway,
        )
        java_updated = to_java_map(
            {
                dimension_name: to_java_map(
                    {
                        hierarchy_name: to_java_map(
                            {
                                name: to_store_field(column, gateway=self.gateway)
                                for name, column in levels.items()
                            },
                            gateway=self.gateway,
                        )
                        for hierarchy_name, levels in hierarchy.items()
                    },
                    gateway=self.gateway,
                )
                for dimension_name, hierarchy in updated.items()
            },
            gateway=self.gateway,
        )
        self._outside_transaction_api().updateHierarchiesForCube(
            cube_name,
            java_updated,
            java_deleted,
        )

    def create_analysis_hierarchy(
        self,
        name: str,
        /,
        *,
        column_identifier: ColumnIdentifier,
        cube_name: str,
    ) -> None:
        """Create an analysis hierarchy from an existing table column."""
        self._outside_transaction_api().createAnalysisHierarchy(
            cube_name,
            name,
            column_identifier.table_identifier.table_name,
            column_identifier.column_name,
        )

    def create_date_hierarchy(
        self,
        name: str,
        /,
        *,
        cube_name: str,
        column_identifier: ColumnIdentifier,
        levels: Mapping[str, str],
    ) -> None:
        self._outside_transaction_api().createDateHierarchy(
            cube_name,
            column_identifier.table_identifier.table_name,
            column_identifier.column_name,
            name,
            to_java_map(levels, gateway=self.gateway),
        )

    def update_hierarchy_dimension(
        self,
        identifier: HierarchyIdentifier,
        new_dimension: str,
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().updateHierarchyCoordinate(
            cube_name,
            identifier._java_description,
            HierarchyIdentifier.from_key(
                (new_dimension, identifier.hierarchy_name)
            )._java_description,
        )

    def update_hierarchy_slicing(
        self,
        identifier: HierarchyIdentifier,
        slicing: bool,  # noqa: FBT001
        /,
        *,
        cube_name: str,
    ) -> None:
        """Update whether the hierarchy is slicing or not."""
        self._outside_transaction_api().setHierarchySlicing(
            cube_name,
            identifier._java_description,
            slicing,
        )

    def update_hierarchy_virtual(
        self,
        identifier: HierarchyIdentifier,
        virtual: bool,  # noqa: FBT001
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().setHierarchyVirtual(
            cube_name,
            identifier._java_description,
            virtual,
        )

    def get_hierarchy_properties(
        self,
        identifier: HierarchyIdentifier,
        *,
        cube_name: str,
        key: str | None,
    ) -> dict[str, JsonValue]:
        java_hierarchy = self._outside_transaction_api().getHierarchy(
            cube_name,
            identifier.dimension_identifier.dimension_name,
            identifier.hierarchy_name,
        )
        if java_hierarchy.isEmpty():
            raise KeyError(identifier.hierarchy_name)
        adapter: TypeAdapter[JsonValue] = get_type_adapter(JsonValue)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
        return {
            name: self._read_hierarchy_property(adapter, value)
            for name, value in java_hierarchy.orElseThrow().customProperties().items()
            if key is None or name == key
        }

    def _read_hierarchy_property(
        self,
        adapter: TypeAdapter[JsonValue],
        value: str,
    ) -> JsonValue:
        try:
            return adapter.validate_json(value)
        except ValidationError:
            return value

    def set_hierarchy_properties(
        self,
        identifier: HierarchyIdentifier,
        properties: Mapping[str, JsonValue],
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().setHierarchyProperties(
            cube_name,
            identifier.dimension_identifier.dimension_name,
            identifier.hierarchy_name,
            to_java_map(
                {k: self._encode_hierarchy_property(v) for k, v in properties.items()},
                gateway=self.gateway,
            ),
        )

    @staticmethod
    def _encode_hierarchy_property(value: JsonValue) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value)

    def update_level_order(
        self,
        identifier: LevelIdentifier,
        order: Order,
        /,
        *,
        cube_name: str,
    ) -> None:
        first_elements = (
            to_java_object_array(order.first_elements, gateway=self.gateway)
            if isinstance(order, CustomOrder)
            else None
        )

        self._outside_transaction_api().updateLevelComparator(
            cube_name,
            identifier._java_description,
            order._key,
            first_elements,
        )

    def delete_level(self, identifier: LevelIdentifier, /, *, cube_name: str) -> None:
        if (
            self._outside_transaction_api()
            .removeLevel(identifier._java_description, cube_name)
            .isEmpty()
        ):
            raise KeyError(identifier.level_name)

    def memory_analysis_export(self, directory: Path, folder: str, /) -> None:
        self._outside_transaction_api().memoryAnalysisExport(str(directory), folder)

    def get_level_data_type(
        self,
        identifier: LevelIdentifier,
        /,
        *,
        cube_name: str,
    ) -> DataType:
        java_hierarchy = self._outside_transaction_api().getHierarchy(
            cube_name,
            identifier.hierarchy_identifier.dimension_identifier.dimension_name,
            identifier.hierarchy_identifier.hierarchy_name,
        )
        assert not java_hierarchy.isEmpty()
        return next(
            _to_data_type(java_level.type())
            for name, java_level in to_python_dict(
                java_hierarchy.orElseThrow().levels()
            ).items()
            if name == identifier.level_name
        )

    def get_level_order(
        self,
        identifier: LevelIdentifier,
        /,
        *,
        cube_name: str,
    ) -> Order:
        java_hierarchy = (
            self._outside_transaction_api()
            .getHierarchy(
                cube_name,
                identifier.hierarchy_identifier.dimension_identifier.dimension_name,
                identifier.hierarchy_identifier.hierarchy_name,
            )
            .orElseThrow()
        )
        java_levels = java_hierarchy.levels()
        java_level = next(
            java_level
            for level_name, java_level in to_python_dict(java_levels).items()
            if level_name == identifier.level_name
        )
        comparator_key = java_level.comparatorPluginKey()
        first_elements = (
            list(java_level.firstMembers())
            if java_level.firstMembers() is not None
            else None
        )

        if comparator_key == CustomOrder(first_elements=["unused"])._key:
            assert first_elements is not None
            return CustomOrder(first_elements=first_elements)

        return NaturalOrder(ascending="reverse" not in comparator_key.lower())

    def set_measure_folder(
        self,
        identifier: MeasureIdentifier,
        folder: str | None,
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().setMeasureFolder(
            folder,
            identifier.measure_name,
            cube_name,
        )

    def set_measure_formatter(
        self,
        identifier: MeasureIdentifier,
        formatter: str | None,
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().setMeasureFormatter(
            formatter,
            identifier.measure_name,
            cube_name,
        )

    def set_measure_visibility(
        self,
        identifier: MeasureIdentifier,
        visible: bool | None,
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().setMeasureVisibility(
            visible,
            identifier.measure_name,
            cube_name,
        )

    def set_measure_description(
        self,
        identifier: MeasureIdentifier,
        description: str | None,
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().setMeasureDescription(
            description,
            identifier.measure_name,
            cube_name,
        )

    def get_measure_data_type(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        cube_name: str,
    ) -> DataType:
        measure = self._outside_transaction_api().getMeasure(
            identifier.measure_name,
            cube_name,
        )
        return _parse_measure_data_type(measure.orElseThrow().type())

    def get_measure_description(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        cube_name: str,
    ) -> str | None:
        measure = self._outside_transaction_api().getMeasure(
            identifier.measure_name,
            cube_name,
        )
        description = measure.orElseThrow().description()
        assert description is None or isinstance(description, str)
        return description

    def get_measure_folder(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        cube_name: str,
    ) -> str | None:
        measure = self._outside_transaction_api().getMeasure(
            identifier.measure_name,
            cube_name,
        )
        folder = measure.orElseThrow().folder()
        assert folder is None or isinstance(folder, str)
        return folder

    def get_measure_formatter(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        cube_name: str,
    ) -> str | None:
        measure = self._outside_transaction_api().getMeasure(
            identifier.measure_name,
            cube_name,
        )
        formatter = measure.orElseThrow().formatter()
        assert formatter is None or isinstance(formatter, str)
        return formatter

    def get_measure_is_visible(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        cube_name: str,
    ) -> bool:
        measure = self._outside_transaction_api().getMeasure(
            identifier.measure_name,
            cube_name,
        )
        visible = measure.orElseThrow().visible()
        assert isinstance(visible, bool)
        return visible

    def get_measure_name(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        cube_name: str,
    ) -> str:
        measure = self._outside_transaction_api().getMeasure(
            identifier.measure_name,
            cube_name,
        )
        if measure.isEmpty():
            raise KeyError(identifier.measure_name)
        name = measure.orElseThrow().name()
        assert isinstance(name, str)
        return name

    def get_measure_names(
        self,
        *,
        cube_name: str,
    ) -> list[str]:
        java_measures = self._outside_transaction_api().getMeasures(
            cube_name,
        )
        measures = to_python_list(java_measures)
        return [str(measure.name()) for measure in measures]

    def copy_measure(
        self,
        identifier: MeasureIdentifier,
        new_identifier: MeasureIdentifier,
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().copyMeasure(
            cube_name,
            identifier.measure_name,
            new_identifier.measure_name,
        )

    def create_measure(  # pylint: disable=too-many-positional-parameters
        self,
        identifier: MeasureIdentifier | None,
        plugin_key: str,
        /,
        *args: Any,
        cube_name: str,
    ) -> MeasureIdentifier:
        java_args = to_java_object_array(
            [self._levels_to_descriptions(arg) for arg in args],
            gateway=self.gateway,
        )
        name = self._outside_transaction_api().registerMeasure(
            cube_name,
            None if identifier is None else identifier.measure_name,
            plugin_key,
            java_args,
        )
        assert isinstance(name, str)
        return MeasureIdentifier(name)

    def register_aggregation_function(
        self,
        *,
        additional_imports: Collection[str],
        additional_methods: Collection[str],
        contribute_source_code: str,
        decontribute_source_code: str | None,
        merge_source_code: str,
        terminate_source_code: str,
        buffer_types: Collection[DataType],
        output_type: DataType,
        plugin_key: str,
    ) -> None:
        """Register a new user defined aggregation function."""
        self._outside_transaction_api().registerUserDefinedAggregateFunction(
            contribute_source_code,
            decontribute_source_code,
            merge_source_code,
            terminate_source_code,
            to_java_string_array(list(buffer_types), gateway=self.gateway),
            output_type,
            plugin_key,
            to_java_string_array(list(additional_imports), gateway=self.gateway),
            to_java_string_array(list(additional_methods), gateway=self.gateway),
        )

    def _levels_to_descriptions(self, arg: Any) -> Any:
        """Recursively convert levels, hierarchies, and columns to their Java descriptions."""
        if isinstance(arg, tuple):
            return to_java_object_array(
                tuple(self._levels_to_descriptions(e) for e in arg),
                gateway=self.gateway,
            )
        if isinstance(arg, Mapping):
            return to_java_map(
                {
                    self._levels_to_descriptions(k): self._levels_to_descriptions(v)
                    for k, v in arg.items()
                },
                gateway=self.gateway,
            )
        if isinstance(arg, list | set):
            return to_java_list(
                [self._levels_to_descriptions(e) for e in arg],
                gateway=self.gateway,
            )
        if isinstance(arg, ColumnIdentifier):
            return to_store_field(arg, gateway=self.gateway)
        return arg

    def aggregated_measure(
        self,
        identifier: MeasureIdentifier | None,
        plugin_key: str,
        /,
        *,
        cube_name: str,
        column_identifier: ColumnIdentifier,
    ) -> MeasureIdentifier:
        """Create a new aggregated measure and return its name."""
        name = self._outside_transaction_api().createAggregatedMeasure(
            cube_name,
            None if identifier is None else identifier.measure_name,
            column_identifier.table_identifier.table_name,
            column_identifier.column_name,
            plugin_key,
        )
        assert isinstance(name, str)
        return MeasureIdentifier(name)

    def delete_measure(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        cube_name: str,
    ) -> None:
        if (
            self._outside_transaction_api()
            .removeMeasure(identifier.measure_name, cube_name)
            .isEmpty()
        ):
            raise KeyError(identifier.measure_name)

    def set_column_default_value(
        self,
        identifier: ColumnIdentifier,
        default_value: Constant | None,
        /,
    ) -> None:
        self._outside_transaction_api().setFieldDefaultValue(
            to_java_object(default_value, gateway=self.gateway),
            identifier.column_name,
            identifier.table_identifier.table_name,
        )
        self.refresh()

    def create_parameter_simulation(
        self,
        *,
        cube_name: str,
        simulation_name: str,
        measures: Mapping[MeasureIdentifier, Constant | None],
        level_identifiers: Collection[LevelIdentifier],
        base_scenario_name: str | None,
    ) -> str:
        """Create a simulation in the cube and return the name of its backing table."""
        java_measures = to_java_map(
            {
                measure_identifier.measure_name: default_value
                for measure_identifier, default_value in measures.items()
            },
            gateway=self.gateway,
        )
        java_levels = to_java_string_array(
            [
                level_identifier._java_description
                for level_identifier in level_identifiers
            ],
            gateway=self.gateway,
        )
        return cast(
            str,
            self._outside_transaction_api().createParameterSimulation(
                cube_name,
                simulation_name,
                java_levels,
                base_scenario_name,
                java_measures,
            ),
        )

    def _inside_transaction(
        self,
        callback: Callable[[], None],
        *,
        scenario_name: str | None,
        source_key: str | None = None,
    ) -> None:
        if (
            get_data_transaction_id(self._session_id) is not None
            or source_key in _REALTIME_SOURCE_KEYS
        ):
            callback()
        else:
            with transact_data(
                allow_nested=True,
                commit=lambda transaction_id: self.end_data_transaction(
                    transaction_id,
                    has_succeeded=True,
                ),
                rollback=lambda transaction_id: self.end_data_transaction(
                    transaction_id,
                    has_succeeded=False,
                ),
                session_id=self._session_id,
                start=lambda: self.start_data_transaction(
                    initiated_by_user=False,
                    scenario_name=scenario_name,
                    table_identifiers=None,
                ),
                table_identifiers=None,
            ):
                callback()

    def block_until_widget_loaded(self, widget_id: str, /) -> None:
        """Block until the widget is loaded."""
        self.py4j_client.blockUntilWidgetLoaded(widget_id)

    def get_shared_context_values(
        self,
        /,
        *,
        cube_name: str,
        key: str | None,
    ) -> dict[str, str]:
        return {
            name: value
            for name, value in to_python_dict(
                self._outside_transaction_api().getCubeShareContextValues(cube_name),
            ).items()
            if key is None or name == key
        }

    def set_shared_context_value(
        self,
        key: str,
        value: str,
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().setCubeSharedContextValue(cube_name, key, value)

    def get_cube_mask(
        self,
        role: str | None,
        /,
        *,
        cube_name: str,
    ) -> dict[str, CubeMaskCondition]:
        included_member_paths = "includedPaths"
        included_members = "includedMembers"
        excluded_member_paths = "excludedPaths"
        excluded_members = "excludedMembers"

        masks = (
            to_python_dict(
                self._outside_transaction_api().getCubeMemberMasking(cube_name)
            )
            if role is None
            else {
                role: self._outside_transaction_api().getCubeMemberMasking(
                    cube_name, role
                )
            }
        )

        return {
            role: condition_from_dnf(
                (
                    [
                        HierarchyMembershipCondition(
                            subject=HierarchyIdentifier._from_java_description(
                                hierarchy_java_description
                            ),
                            operator="in"
                            if inclusion_or_exclusion_type == included_member_paths
                            else "not in",
                            member_paths=to_python_set(
                                mask[inclusion_or_exclusion_type]
                            ),
                            # Pass real level names when migrating to GraphQL.
                            level_names=["__unused__"],
                        )
                        for hierarchy_java_description, mask in to_python_dict(
                            mask_from_hierarchy_java_description
                        ).items()
                        for inclusion_or_exclusion_type in sorted(mask, reverse=True)
                        if (
                            inclusion_or_exclusion_type
                            in {included_member_paths, excluded_member_paths}
                            and mask[inclusion_or_exclusion_type]
                        )
                    ]
                    + [
                        MembershipCondition.of(
                            subject=HierarchyIdentifier._from_java_description(
                                hierarchy_java_description
                            ),
                            operator="in"
                            if inclusion_or_exclusion_type == included_members
                            else "not in",
                            elements=to_python_set(mask[inclusion_or_exclusion_type]),
                        )
                        for hierarchy_java_description, mask in to_python_dict(
                            mask_from_hierarchy_java_description
                        ).items()
                        for inclusion_or_exclusion_type in sorted(mask, reverse=True)
                        if (
                            inclusion_or_exclusion_type
                            in {included_members, excluded_members}
                            and mask[inclusion_or_exclusion_type]
                        )
                    ],
                )
            )
            for role, mask_from_hierarchy_java_description in masks.items()
        }

    def set_cube_mask(
        self,
        role: str,
        /,
        *,
        cube_name: str,
        included_members: Mapping[str, AbstractSet[Scalar]],
        included_member_paths: Mapping[str, AbstractSet[tuple[Scalar, ...]]],
        excluded_members: Mapping[str, AbstractSet[Scalar]],
        excluded_member_paths: Mapping[str, AbstractSet[tuple[Scalar, ...]]],
    ) -> None:
        java_included_member_paths = to_java_map(
            {
                hierarchy_java_description: to_java_list(
                    [
                        to_java_list(
                            [
                                to_java_object(member, gateway=self.gateway)
                                for member in member_path
                            ],
                            gateway=self.gateway,
                        )
                        for member_path in member_paths
                    ],
                    gateway=self.gateway,
                )
                for hierarchy_java_description, member_paths in included_member_paths.items()
            },
            gateway=self.gateway,
        )

        java_included_members = to_java_map(
            {
                hierarchy_java_description: to_java_list(
                    [
                        to_java_object(member, gateway=self.gateway)
                        for member in members
                    ],
                    gateway=self.gateway,
                )
                for hierarchy_java_description, members in included_members.items()
            },
            gateway=self.gateway,
        )

        java_excluded_member_paths = to_java_map(
            {
                hierarchy_java_description: to_java_list(
                    [
                        to_java_list(
                            [
                                to_java_object(member, gateway=self.gateway)
                                for member in member_path
                            ],
                            gateway=self.gateway,
                        )
                        for member_path in member_paths
                    ],
                    gateway=self.gateway,
                )
                for hierarchy_java_description, member_paths in excluded_member_paths.items()
            },
            gateway=self.gateway,
        )

        java_excluded_members = to_java_map(
            {
                hierarchy_java_description: to_java_list(
                    [
                        to_java_object(member, gateway=self.gateway)
                        for member in members
                    ],
                    gateway=self.gateway,
                )
                for hierarchy_java_description, members in excluded_members.items()
            },
            gateway=self.gateway,
        )

        self._outside_transaction_api().setCubeMasking(
            cube_name,
            role,
            java_included_member_paths,
            java_excluded_member_paths,
            java_included_members,
            java_excluded_members,
        )

    def external_api(self, key: str, /) -> Any:
        return self._outside_transaction_api().externalDatabaseApi(key)

    def _to_java_table_id(self, identifier: ExternalTableIdentifier, /) -> JavaObject:
        return self.jvm.com.activeviam.database.sql.api.schema.SqlTableId(
            identifier.catalog_name,
            identifier.schema_name,
            identifier.table_name,
        )

    def _to_java_emulated_time_travel_table_config(
        self, config: EmulatedTimeTravelTableConfig, /
    ) -> JavaObject:
        return self.jvm.io.atoti.runtime.internal.directquery.EmulatedTimeTravelTableDescription(
            config.valid_from_column_name,
            config.valid_to_column_name,
        )

    def _to_external_table_identifier(
        self,
        java_table_id: Any,
        /,
    ) -> ExternalTableIdentifier:
        return ExternalTableIdentifier(
            java_table_id.getCatalogName(),
            java_table_id.getSchemaName(),
            java_table_id.getTableName(),
        )

    def connect_to_database(
        self,
        key: str,
        /,
        *,
        url: str | None,
        password: str | None,
        options: Mapping[str, str | None],
    ) -> None:
        options = to_java_map(options, gateway=self.gateway)
        self.external_api(key).connectToDatabase(url, password, options)

    def get_external_tables(
        self,
        key: str,
        /,
    ) -> set[ExternalTableIdentifier]:
        catalogs = self.external_api(key).getTables()
        return {
            ExternalTableIdentifier(
                catalog_name,
                schema_name,
                table_name,
            )
            for catalog_name, schemas in to_python_dict(catalogs).items()
            for schema_name, tables in to_python_dict(schemas).items()
            for table_name in to_python_list(tables)
        }

    def get_external_table_schema(
        self,
        key: str,
        /,
        *,
        identifier: ExternalTableIdentifier,
    ) -> dict[str, DataType]:
        schema = self.external_api(key).getTableSchema(
            self._to_java_table_id(identifier),
        )
        return _convert_java_column_types(schema)

    def add_external_table(
        self,
        key: str,
        /,
        *,
        clustering_columns: AbstractSet[str] | None,
        columns: Mapping[str, str],
        identifier: ExternalTableIdentifier,
        keys: Sequence[str] | None,
        local_table_identifier: TableIdentifier,
        emulated_time_travel: EmulatedTimeTravelTableConfig | None,
    ) -> None:
        java_keys = None if keys is None else to_java_list(keys, gateway=self.gateway)
        java_clustering_columns = (
            None
            if clustering_columns is None
            else to_java_list(clustering_columns, gateway=self.gateway)
        )
        java_columns = to_java_map(columns, gateway=self.gateway)
        self.external_api(key).addTable(
            self._to_java_table_id(identifier),
            local_table_identifier.table_name,
            java_keys,
            java_columns,
            java_clustering_columns,
            to_json(emulated_time_travel).decode(),
        )

    def add_external_table_with_multi_row_arrays(
        self,
        key: str,
        /,
        *,
        array_columns: Collection[str],
        clustering_columns: AbstractSet[str] | None,
        identifier: ExternalTableIdentifier,
        columns: Mapping[str, str],
        index_column: str,
        local_table_identifier: TableIdentifier,
        emulated_time_travel: EmulatedTimeTravelTableConfig | None,
    ) -> None:
        java_clustering_columns = (
            None
            if clustering_columns is None
            else to_java_list(clustering_columns, gateway=self.gateway)
        )
        java_columns = to_java_map(columns, gateway=self.gateway)
        self.external_api(key).addTableWithMultiRowArray(
            self._to_java_table_id(identifier),
            local_table_identifier.table_name,
            java_columns,
            java_clustering_columns,
            index_column,
            to_java_list(array_columns, gateway=self.gateway),
            to_json(emulated_time_travel).decode(),
        )

    def add_external_multi_column_array_table(
        self,
        key: str,
        /,
        *,
        column_prefixes: Collection[str],
        clustering_columns: AbstractSet[str] | None,
        columns: Mapping[str, str],
        identifier: ExternalTableIdentifier,
        keys: Sequence[str] | None,
        local_table_identifier: TableIdentifier,
        emulated_time_travel: EmulatedTimeTravelTableConfig | None,
    ) -> None:
        java_keys = None if keys is None else to_java_list(keys, gateway=self.gateway)
        java_column_prefixes = to_java_list(column_prefixes, gateway=self.gateway)
        java_clustering_columns = (
            None
            if clustering_columns is None
            else to_java_list(clustering_columns, gateway=self.gateway)
        )
        java_columns = to_java_map(columns, gateway=self.gateway)

        self.external_api(key).addTableWithMultiColumnArray(
            self._to_java_table_id(identifier),
            local_table_identifier.table_name,
            java_keys,
            java_columns,
            java_clustering_columns,
            java_column_prefixes,
            to_json(emulated_time_travel).decode(),
        )

    def _convert_python_measure_mapping_to_java(
        self,
        measure_mapping: ExternalMeasure,
        /,
    ) -> Any:
        return (
            self.jvm.io.atoti.runtime.internal.directquery.impl.MeasureMappingDescription.builder()
            .aggregationKey(measure_mapping.aggregation_key)
            .originColumns(
                to_java_list(
                    [
                        to_store_field(
                            identify(granular_identifier),
                            gateway=self.gateway,
                        )
                        for granular_identifier in measure_mapping.granular_columns
                    ],
                    gateway=self.gateway,
                ),
            )
            .targetColumns(
                to_java_list(
                    [
                        identify(col).column_name
                        for col in measure_mapping.aggregate_columns
                    ],
                    gateway=self.gateway,
                ),
            )
            .build()
        )

    def _convert_java_measure_mapping_to_python(
        self,
        java_measure_mapping: Any,
        /,
        *,
        aggregate_table_identifier: ExternalTableIdentifier,
    ) -> ExternalMeasure:
        return ExternalMeasure(
            aggregation_key=java_measure_mapping.aggregationKey(),
            granular_columns=[
                _convert_store_field_to_column_identifier(column)
                for column in to_python_list(java_measure_mapping.originColumns())
            ],
            aggregate_columns=[
                ExternalColumnIdentifier(aggregate_table_identifier, column_name)
                for column_name in to_python_list(java_measure_mapping.targetColumns())
            ],
        )

    def _convert_python_external_aggregate_table_to_java(
        self,
        external_aggregate_table: ExternalAggregateTable,
        /,
    ) -> JavaObject:
        granular_table_name = identify(
            external_aggregate_table.granular_table,
        ).table_name
        aggregate_table_id = self._to_java_table_id(
            identify(external_aggregate_table.aggregate_table),
        )
        mapping = to_java_map(
            {
                identify(column): identify(external_column).column_name
                for column, external_column in external_aggregate_table.mapping.items()
            },
            gateway=self.gateway,
        )
        measures = to_java_list(
            [
                self._convert_python_measure_mapping_to_java(measure)
                for measure in external_aggregate_table.measures
            ],
            gateway=self.gateway,
        )
        filters = self._java_map_from_constant_condition(
            external_aggregate_table.filter,
            get_key=lambda identifier: to_store_field(identifier, gateway=self.gateway),
        )
        java_emulated_time_travel_table_config = (
            None
            if external_aggregate_table.time_travel is None
            else self._to_java_emulated_time_travel_table_config(
                external_aggregate_table.time_travel
            )
        )
        return (
            self.jvm.io.atoti.runtime.internal.directquery.impl.AggregateTableDescription.builder()
            .originBaseTableName(granular_table_name)
            .tableId(aggregate_table_id)
            .groupByFields(mapping)
            .measureMappings(measures)
            .filters(filters)
            .emulatedTimeTravel(java_emulated_time_travel_table_config)
            .build()
        )

    def _convert_java_external_aggregate_table(
        self,
        description: Any,
        /,
    ) -> ExternalAggregateTable:
        aggregate_table_identifier = self._to_external_table_identifier(
            description.tableId(),
        )
        mapping: Mapping[
            Identifiable[ColumnIdentifier],
            Identifiable[ExternalColumnIdentifier],
        ] = {
            _convert_store_field_to_column_identifier(
                projected_column,
            ): ExternalColumnIdentifier(
                self._to_external_table_identifier(description.tableId()),
                projection_column_name,
            )
            for projected_column, projection_column_name in to_python_dict(
                description.groupByFields(),
            ).items()
        }
        return ExternalAggregateTable(
            granular_table=TableIdentifier(description.originBaseTableName()),
            aggregate_table=aggregate_table_identifier,
            mapping=mapping,
            measures=[
                self._convert_java_measure_mapping_to_python(
                    java_measure_mapping,
                    aggregate_table_identifier=aggregate_table_identifier,
                )
                for java_measure_mapping in to_python_list(
                    description.measureMappings(),
                )
            ],
            filter=_constant_condition_from_java_mapping(
                to_python_dict(description.filters()),
                identify=lambda key: _convert_store_field_to_column_identifier(key),
            ),
            time_travel=_convert_java_emulated_time_travel_table(
                description.emulatedTimeTravel()
            ),
        )

    def get_external_aggregate_tables(
        self,
        *,
        key: str | None,
    ) -> dict[str, ExternalAggregateTable]:
        java_aggregate_tables = self._outside_transaction_api().getAggregateTables()
        return {
            name: self._convert_java_external_aggregate_table(description)
            for name, description in to_python_dict(java_aggregate_tables).items()
            if key is None or name == key
        }

    def set_external_aggregate_tables(
        self,
        external_aggregate_tables: Mapping[str, ExternalAggregateTable],
        /,
    ) -> None:
        self._outside_transaction_api().setAggregateTables(
            to_java_map(
                {
                    name: self._convert_python_external_aggregate_table_to_java(
                        aggregate_table,
                    )
                    for name, aggregate_table in external_aggregate_tables.items()
                },
                gateway=self.gateway,
            ),
        )

    def remove_external_aggregate_tables(
        self,
        names: Collection[str],
        /,
    ) -> None:
        self._outside_transaction_api().removeAggregateTables(
            to_java_list(
                names,
                gateway=self.gateway,
            ),
        )

    def derive_external_aggregate_table(
        self,
        provider: AggregateProvider,
        /,
        *,
        cube_name: str,
        key: str,
        table_identifier: ExternalTableIdentifier,
    ) -> ExternalAggregateTable:
        java_aggregate_provider = self._convert_python_aggregate_provider_to_java(
            provider,
        )
        java_aggregate_table = self.external_api(key).deriveAggregateTable(
            cube_name,
            java_aggregate_provider,
            table_identifier.catalog_name,
            table_identifier.schema_name,
            table_identifier.table_name,
        )
        return self._convert_java_external_aggregate_table(java_aggregate_table)

    def generate_external_aggregate_table_sql(
        self,
        aggregate_table: ExternalAggregateTable,
        /,
        *,
        key: str,
    ) -> ExternalAggregateTableSql:
        java_aggregate_table = self._convert_python_external_aggregate_table_to_java(
            aggregate_table,
        )
        java_sql_queries_map = self.external_api(key).getSqlForAggregateTableCreation(
            java_aggregate_table,
        )
        python_sql_queries = {
            key.toString(): value
            for key, value in to_python_dict(java_sql_queries_map).items()
        }
        return ExternalAggregateTableSql(
            create=python_sql_queries["CREATE"],
            insert=python_sql_queries["FEED"],
        )

    def get_external_database_cache(self, key: str, /) -> bool | None:
        return cast(bool | None, self.external_api(key).getCache())

    def set_external_database_cache(self, key: str, /, *, cache: bool) -> None:
        self.external_api(key).setCache(cache)

    def synchronize_with_external_database(self) -> None:
        self.py4j_client.synchronizeWithDatabase()

    def _convert_python_condition_to_java_column_conditions(
        self,
        condition: ConstantColumnCondition,
    ) -> object:
        return to_java_list(
            [
                to_java_list(
                    [
                        self._build_java_column_condition(leaf_condition)  # type: ignore[arg-type]
                        for leaf_condition in conjunct_conditions
                    ],
                    gateway=self.gateway,
                )
                for conjunct_conditions in dnf_from_condition(condition)
            ],
            gateway=self.gateway,
        )

    def set_hierarchy_dimension_default(
        self,
        identifier: HierarchyIdentifier,
        dimension_default: bool,  # noqa: FBT001
        /,
        *,
        cube_name: str,
    ) -> None:
        self._outside_transaction_api().setHierarchyAsDimensionDefault(
            dimension_default,
            identifier.hierarchy_name,
            identifier.dimension_identifier.dimension_name,
            cube_name,
        )
