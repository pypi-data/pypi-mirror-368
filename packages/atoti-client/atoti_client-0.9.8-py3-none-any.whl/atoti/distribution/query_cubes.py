from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from .._client import Client
from .._collections import DelegatingConvertingMapping, SupportsUncheckedMappingLookup
from .._identification import QueryCubeIdentifier, QueryCubeName, identify
from .._identification.level_key import java_description_from_level_key
from .._ipython import ReprJson, ReprJsonable
from .query_cube import QueryCube
from .query_cube_definition import QueryCubeDefinition


@final
class QueryCubes(
    SupportsUncheckedMappingLookup[QueryCubeName, QueryCubeName, QueryCube],
    DelegatingConvertingMapping[
        QueryCubeName, QueryCubeName, QueryCube, QueryCubeDefinition
    ],
    ReprJsonable,
):
    r"""Manage the :class:`~atoti.QueryCube`\ s of a :class:`~atoti.QuerySession`."""

    def __init__(self, *, client: Client):
        self._client: Final = client

    @override
    def _create_lens(self, key: QueryCubeName, /) -> QueryCube:
        return QueryCube(QueryCubeIdentifier(key), client=self._client)

    @override
    def _get_unambiguous_keys(
        self, *, key: QueryCubeName | None
    ) -> list[QueryCubeName]:
        if key is None:
            output = self._client._require_graphql_client().get_cubes()
            return [cube.name for cube in output.data_model.cubes]

        output = self._client._require_graphql_client().find_cube(cube_name=key)  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
        cube = output.data_model.cube  # type: ignore[attr-defined]
        return [] if cube is None else [cube.name]

    @override
    def _update_delegate(
        self,
        other: Mapping[QueryCubeName, QueryCubeDefinition],
        /,
    ) -> None:
        py4j_client = self._client._require_py4j_client()

        for cube_name, cube_definition in other.items():
            cluster_identifier = identify(cube_definition.cluster)
            application_names = cube_definition.application_names

            if application_names is None:
                application_names = py4j_client.get_cluster_application_names(
                    cluster_identifier
                )

            py4j_client.create_query_cube(
                cube_name,
                application_names=application_names,
                catalog_names=cube_definition.catalog_names,
                cluster_name=cluster_identifier.cluster_name,
                distribution_levels=[
                    java_description_from_level_key(lvl)
                    for lvl in cube_definition.distributing_levels
                ],
                allow_data_duplication=cube_definition.allow_data_duplication,
            )

        py4j_client.refresh()

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[QueryCubeName], /) -> None:
        raise NotImplementedError("Deleting query cubes is not supported yet.")

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            {name: cube._repr_json_()[0] for name, cube in self.items()},
            {"expanded": False, "root": "Cubes"},
        )
