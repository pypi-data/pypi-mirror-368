from __future__ import annotations

import operator
from typing import Final, final

from typing_extensions import deprecated, override

from ._client import Client
from ._collections import (
    DelegatingKeyDisambiguatingMapping,
    SupportsUncheckedMappingLookup,
)
from ._cube_discovery import get_discovery
from ._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from ._identification import (
    RESERVED_DIMENSION_NAMES as _RESERVED_DIMENSION_NAMES,
    CubeIdentifier,
    LevelIdentifier,
    LevelKey,
    LevelUnambiguousKey,
)
from ._identification.level_key import normalize_level_key
from ._ipython import KeyCompletable, ReprJson, ReprJsonable
from .hierarchies import Hierarchies
from .level import Level


@final
class Levels(
    SupportsUncheckedMappingLookup[LevelKey, LevelUnambiguousKey, Level],
    DelegatingKeyDisambiguatingMapping[LevelKey, LevelUnambiguousKey, Level],
    KeyCompletable,
    ReprJsonable,
):
    r"""Flat representation of all the :class:`~atoti.Level`\ s in a :class:`~atoti.Cube`."""

    def __init__(
        self,
        cube_identifier: CubeIdentifier,
        /,
        *,
        client: Client,
        hierarchies: Hierarchies,
    ) -> None:
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier
        self._hierarchies: Final = hierarchies

    @override
    def _create_lens(self, key: LevelUnambiguousKey, /) -> Level:
        return Level(
            LevelIdentifier.from_key(key),
            client=self._client,
            cube_identifier=self._cube_identifier,
        )

    @override
    def _get_unambiguous_keys(
        self, *, key: LevelKey | None
    ) -> list[LevelUnambiguousKey]:
        dimension_name, hierarchy_name, level_name = (
            (None, None, None) if key is None else normalize_level_key(key)
        )
        graphql_client = self._client._graphql_client

        # Remove `self._client._py4j_client is None` once `QuerySession`s are supported.
        if self._client._py4j_client is None or graphql_client is None:
            discovery = get_discovery(client=self._client)
            return [
                (dimension.name, hierarchy.name, level.name)
                for dimension in discovery.cubes[
                    self._cube_identifier.cube_name
                ].dimensions
                if dimension.name not in _RESERVED_DIMENSION_NAMES
                and (dimension_name is None or dimension.name == dimension_name)
                for hierarchy in dimension.hierarchies
                if hierarchy_name is None or hierarchy.name == hierarchy_name
                for level in hierarchy.levels
                if (level.type != "ALL")
                and (level_name is None or level.name == level_name)
            ]

        if level_name is None:
            output = graphql_client.get_levels(
                cube_name=self._cube_identifier.cube_name
            )
            return [
                (dimension.name, hierarchy.name, level.name)
                for dimension in output.data_model.cube.dimensions
                if dimension.name not in _RESERVED_DIMENSION_NAMES
                for hierarchy in dimension.hierarchies
                for level in hierarchy.levels
                if level.type.value != "ALL"
            ]

        if hierarchy_name is None:
            output = graphql_client.find_level_across_hierarchies(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
                cube_name=self._cube_identifier.cube_name,
                level_name=level_name,
            )
            return [
                (
                    dimension.name,
                    hierarchy.name,
                    hierarchy.level.name,  # type: ignore[attr-defined]
                )
                for dimension in output.data_model.cube.dimensions
                if dimension.name not in _RESERVED_DIMENSION_NAMES
                for hierarchy in dimension.hierarchies
                if hierarchy.level and hierarchy.level.type.value != "ALL"  # type: ignore[attr-defined]
            ]

        if dimension_name is None:
            output = graphql_client.find_level_across_dimensions(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
                cube_name=self._cube_identifier.cube_name,
                hierarchy_name=hierarchy_name,
                level_name=level_name,
            )
            return [
                (
                    dimension.name,
                    dimension.hierarchy.name,  # type: ignore[attr-defined]
                    dimension.hierarchy.level.name,  # type: ignore[attr-defined]
                )
                for dimension in output.data_model.cube.dimensions
                if dimension.name not in _RESERVED_DIMENSION_NAMES
                and dimension.hierarchy  # type: ignore[attr-defined]
                and dimension.hierarchy.level  # type: ignore[attr-defined]
                and dimension.hierarchy.level.type.value != "ALL"  # type: ignore[attr-defined]
            ]

        output = graphql_client.find_level(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
            cube_name=self._cube_identifier.cube_name,
            dimension_name=dimension_name,
            hierarchy_name=hierarchy_name,
            level_name=level_name,
        )
        dimension = output.data_model.cube.dimension  # type: ignore[attr-defined]
        level = dimension and dimension.hierarchy and dimension.hierarchy.level

        if (
            level is None
            or level.hierarchy.dimension.name in _RESERVED_DIMENSION_NAMES
            or level.type.value == "ALL"
        ):
            return []

        return [LevelIdentifier._from_graphql(level).key]

    @override
    def _repr_json_(self) -> ReprJson:
        # Use the dimension/hierarchy/level in the map key to make it unique.
        data = {
            f"{level.name} ({level.dimension}/{level.hierarchy})": level._repr_json_()[
                0
            ]
            for hierarchy in self._hierarchies.values()
            for level in hierarchy.values()
        }
        sorted_data = dict(sorted(data.items(), key=operator.itemgetter(0)))
        return (
            sorted_data,
            {
                "expanded": True,
                "root": "Levels",
            },
        )

    @deprecated(
        "Deleting a `Level` is deprecated, redefine its `Hierarchy` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def __delitem__(self, key: LevelKey, /) -> None:
        py4j_client = self._client._require_py4j_client()
        level = self[key]
        py4j_client.delete_level(
            level._identifier,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.refresh()
