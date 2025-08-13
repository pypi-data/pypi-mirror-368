from collections.abc import Callable, Mapping, Set as AbstractSet
from types import EllipsisType
from typing import Final, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingConvertingMapping, SupportsUncheckedMappingLookup
from ._cube_definition import CubeDefinition, _CreationMode
from ._cube_discovery import get_discovery
from ._graphql_client import (
    CreateCubeInput,
    HierarchiesCreationMode,
    MeasuresCreationMode,
)
from ._identification import ApplicationName, CubeIdentifier, CubeName, identify
from ._ipython import ReprJson, ReprJsonable
from ._session_id import SessionId
from .cube import Cube


def _get_application_name(
    application_name: ApplicationName | EllipsisType | None,
    /,
    *,
    cube_name: str,
) -> ApplicationName | None:
    match application_name:
        case str():
            return application_name
        case EllipsisType():
            return cube_name
        case None:
            return None


def _get_deprecated_creation_mode(  # type: ignore[return]
    *, hierarchies: _CreationMode, measures: _CreationMode
) -> str:
    match hierarchies, measures:
        case "auto", "auto":
            return "AUTO"
        case "auto", "manual":
            return "NO_MEASURES"
        case "manual", "auto":
            raise NotImplementedError(
                "Cannot automatically create measures without also automatically creating hierarchies."
            )
        case "manual", "manual":
            return "MANUAL"


def _get_hierarchies_creation_mode(mode: _CreationMode, /) -> HierarchiesCreationMode:
    match mode:
        case "auto":
            return HierarchiesCreationMode.AUTO
        case "manual":
            return HierarchiesCreationMode.MANUAL


def _get_measures_creation_mode(mode: _CreationMode, /) -> MeasuresCreationMode:
    match mode:
        case "auto":
            return MeasuresCreationMode.AUTO
        case "manual":
            return MeasuresCreationMode.MANUAL


def _get_create_cube_input(
    definition: CubeDefinition, /, *, identifier: CubeIdentifier
) -> CreateCubeInput:
    graphql_input = CreateCubeInput(
        catalog_names=list(definition.catalog_names),
        cube_name=identifier.cube_name,
        fact_table_name=identify(definition.fact_table).table_name,
        hierarchies=_get_hierarchies_creation_mode(definition.hierarchies),
        measures=_get_measures_creation_mode(definition.measures),
    )

    application_name = _get_application_name(
        definition.application_name, cube_name=identifier.cube_name
    )
    if application_name is not None:
        graphql_input.application_name = application_name

    if definition.id_in_cluster is not None:
        graphql_input.id_in_cluster = definition.id_in_cluster

    if definition.priority is not None:
        graphql_input.priority = definition.priority

    return graphql_input


@final
class Cubes(
    SupportsUncheckedMappingLookup[CubeName, CubeName, Cube],
    DelegatingConvertingMapping[CubeName, CubeName, Cube, CubeDefinition],
    ReprJsonable,
):
    r"""Manage the :class:`~atoti.Cube`\ s of a :class:`~atoti.Session`."""

    def __init__(
        self,
        *,
        client: Client,
        get_widget_creation_code: Callable[[], str | None],
        session_id: SessionId,
    ) -> None:
        self._client: Final = client
        self._get_widget_creation_code: Final = get_widget_creation_code
        self._session_id: Final = session_id

    @override
    def _create_lens(self, key: CubeName, /) -> Cube:
        return Cube(
            CubeIdentifier(key),
            client=self._client,
            get_widget_creation_code=self._get_widget_creation_code,
            session_id=self._session_id,
        )

    @override
    def _get_unambiguous_keys(self, *, key: CubeName | None) -> list[CubeName]:
        # Remove `self._client._py4j_client is None` once `QuerySession`s are supported.
        if self._client._py4j_client is None or self._client._graphql_client is None:
            discovery = get_discovery(client=self._client)
            return [
                cube_name
                for cube_name in discovery.cubes
                if key is None or cube_name == key
            ]

        if key is None:
            output = self._client._graphql_client.get_cubes()
            return [cube.name for cube in output.data_model.cubes]

        output = self._client._graphql_client.find_cube(cube_name=key)  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
        cube = output.data_model.cube  # type: ignore[attr-defined]
        return [] if cube is None else [cube.name]

    @override
    def _update_delegate(
        self,
        other: Mapping[CubeName, CubeDefinition],
        /,
    ) -> None:
        py4j_api = self._client._require_py4j_client()

        if any(definition.filter is not None for definition in other.values()):
            for name, definition in other.items():
                py4j_api.create_cube_from_table(
                    name,
                    application_name=_get_application_name(
                        definition.application_name, cube_name=name
                    ),
                    catalog_names=definition.catalog_names,
                    filter=definition.filter,
                    mode=_get_deprecated_creation_mode(
                        hierarchies=definition.hierarchies, measures=definition.measures
                    ),
                    table_identifier=identify(definition.fact_table),
                    id_in_cluster=definition.id_in_cluster,
                    priority=definition.priority,
                )

            py4j_api.refresh()
        else:
            graphql_client = self._client._require_graphql_client()

            with graphql_client.mutation_batcher.batch():
                for name, definition in other.items():
                    graphql_input = _get_create_cube_input(
                        definition, identifier=CubeIdentifier(name)
                    )
                    graphql_client.create_cube(input=graphql_input)

        if py4j_api.get_readiness():
            for name in other:
                # AutoJoin distributed clusters if the session has been marked as ready
                py4j_api.auto_join_distributed_clusters(cube_name=name)
            py4j_api.refresh()

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[CubeName], /) -> None:
        py4j_api = self._client._require_py4j_client()

        for key in keys:
            py4j_api.delete_cube(key)

    @override
    def _repr_json_(self) -> ReprJson:
        """Return the JSON representation of cubes."""
        return (
            {name: cube._repr_json_()[0] for name, cube in sorted(self.items())},
            {"expanded": False, "root": "Cubes"},
        )
