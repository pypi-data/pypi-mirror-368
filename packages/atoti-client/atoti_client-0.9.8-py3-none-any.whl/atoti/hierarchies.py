from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence, Set as AbstractSet
from typing import Final, TypeAlias, final

from typing_extensions import override

from ._client import Client
from ._collections import (
    DelegatingConvertingMapping,
    SupportsUncheckedMappingLookup,
)
from ._cube_discovery import get_discovery
from ._get_selection_field_from_column_identifier import (
    get_selection_field_from_column_identifier,
)
from ._graphql_client import (
    CreateHierarchyInput,
    DeleteHierarchyInput,
    HierarchyDefinition,
    SelectionHierarchyDefinition,
    SelectionHierarchyLevelDefinition,
    create_delete_status_validator,
)
from ._identification import (
    RESERVED_DIMENSION_NAMES as _RESERVED_DIMENSION_NAMES,
    ColumnIdentifier,
    CubeIdentifier,
    DimensionName,
    HierarchyIdentifier,
    HierarchyKey,
    HierarchyName,
    HierarchyUnambiguousKey,
    Identifiable,
    LevelIdentifier,
    LevelName,
    identify,
)
from ._ipython import ReprJson, ReprJsonable
from ._selection_field import SelectionField
from .hierarchy import Hierarchy
from .level import _get_selection_field as _get_level_selection_field

_HierarchyConvertibleElement: TypeAlias = (
    Identifiable[ColumnIdentifier] | Identifiable[LevelIdentifier]
)
_HierarchyConvertible: TypeAlias = (
    Sequence[_HierarchyConvertibleElement]
    | Mapping[LevelName, _HierarchyConvertibleElement]
)


def _get_column_identifier(  # type: ignore[return]
    element: _HierarchyConvertibleElement,
    /,
    *,
    client: Client,
    cube_identifier: CubeIdentifier,
) -> ColumnIdentifier:
    match identify(element):
        case ColumnIdentifier() as column_identifier:
            return column_identifier
        case LevelIdentifier() as level_identifier:
            selection_field = _get_level_selection_field(
                level_identifier, client=client, cube_identifier=cube_identifier
            )
            assert selection_field is not None
            return selection_field.column_identifier


def _infer_dimension_name(element: _HierarchyConvertibleElement, /) -> DimensionName:  # type: ignore[return]
    match identify(element):
        case ColumnIdentifier() as column_identifier:
            return column_identifier.table_identifier.table_name
        case LevelIdentifier() as level_identifier:
            return level_identifier.hierarchy_identifier.dimension_identifier.dimension_name


def _normalize_key(key: HierarchyKey, /) -> tuple[DimensionName | None, HierarchyName]:
    return (None, key) if isinstance(key, str) else key


def _get_selection_field_from_level_identifier(
    level_identifiers: AbstractSet[LevelIdentifier],
    /,
    *,
    client: Client,
    cube_identifier: CubeIdentifier,
) -> dict[LevelIdentifier, SelectionField]:
    selection_field_identifier_from_level_identifier: dict[
        LevelIdentifier, SelectionField
    ] = {}

    for level_identifier in level_identifiers:
        selection_field = _get_level_selection_field(
            level_identifier, client=client, cube_identifier=cube_identifier
        )
        if selection_field is None:
            raise RuntimeError(f"{level_identifier} has no selection field.")
        selection_field_identifier_from_level_identifier[level_identifier] = (
            selection_field
        )

    return selection_field_identifier_from_level_identifier


def _get_selection_field_from_identifier(
    dimensions: Mapping[
        DimensionName,
        Mapping[HierarchyName, Mapping[LevelName, ColumnIdentifier | LevelIdentifier]],
    ],
    /,
    *,
    client: Client,
    cube_identifier: CubeIdentifier,
) -> dict[ColumnIdentifier | LevelIdentifier, SelectionField]:
    column_identifiers: set[ColumnIdentifier] = set()
    level_identifiers: set[LevelIdentifier] = set()
    for hierarchies in dimensions.values():
        for levels in hierarchies.values():
            for identifier in levels.values():
                match identifier:
                    case ColumnIdentifier():
                        column_identifiers.add(identifier)
                    case LevelIdentifier():
                        level_identifiers.add(identifier)
    return {
        **get_selection_field_from_column_identifier(  # type: ignore[dict-item]
            column_identifiers,
            client=client,
            cube_identifier=cube_identifier,
        ),
        **_get_selection_field_from_level_identifier(  # type: ignore[dict-item]
            level_identifiers,
            client=client,
            cube_identifier=cube_identifier,
        ),
    }


def _get_create_hierarchy_input(
    levels: Mapping[LevelName, ColumnIdentifier | LevelIdentifier],
    /,
    *,
    cube_identifier: CubeIdentifier,
    identifier: HierarchyIdentifier,
    selection_field_from_identifier: Mapping[
        ColumnIdentifier | LevelIdentifier, SelectionField
    ],
) -> CreateHierarchyInput:
    return CreateHierarchyInput(
        cube_name=cube_identifier.cube_name,
        definition=HierarchyDefinition(
            selection=SelectionHierarchyDefinition(
                levels=[
                    SelectionHierarchyLevelDefinition(
                        level_name=level_name,
                        selection_field_identifier=selection_field_from_identifier[
                            identifier
                        ]._identifier._graphql_input,
                    )
                    for level_name, identifier in levels.items()
                ]
            )
        ),
        hierarchy_identifier=identifier._graphql_input,
    )


@final
class Hierarchies(
    SupportsUncheckedMappingLookup[HierarchyKey, HierarchyUnambiguousKey, Hierarchy],
    DelegatingConvertingMapping[
        HierarchyKey,
        HierarchyUnambiguousKey,
        Hierarchy,
        _HierarchyConvertible,
    ],
    ReprJsonable,
):
    """Manage the hierarchies of a :class:`~atoti.Cube`.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> prices_df = pd.DataFrame(
        ...     columns=["Nation", "City", "Color", "Price"],
        ...     data=[
        ...         ("France", "Paris", "red", 20.0),
        ...         ("France", "Lyon", "blue", 15.0),
        ...         ("France", "Toulouse", "green", 10.0),
        ...         ("UK", "London", "red", 20.0),
        ...         ("UK", "Manchester", "blue", 15.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(prices_df, table_name="Prices")
        >>> cube = session.create_cube(table, mode="manual")
        >>> h = cube.hierarchies
        >>> h["Nation"] = {"Nation": table["Nation"]}
        >>> list(h)
        [('Prices', 'Nation')]

        A hierarchy can be renamed by copying it and deleting the old one:

        >>> h["Country"] = h["Nation"]
        >>> del h["Nation"]
        >>> list(h)
        [('Prices', 'Country')]
        >>> list(h["Country"])
        ['Nation']

        :meth:`~dict.update` can be used to batch hierarchy creation operations for improved performance:

        >>> h.update(
        ...     {
        ...         ("Geography", "Geography"): [table["Nation"], table["City"]],
        ...         "Color": {"Color": table["Color"]},
        ...     }
        ... )
        >>> sorted(h)
        [('Geography', 'Geography'), ('Prices', 'Color'), ('Prices', 'Country')]

    See Also:
        :class:`~atoti.Hierarchy` to configure existing hierarchies.
    """

    def __init__(self, cube_identifier: CubeIdentifier, /, *, client: Client) -> None:
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier

    @override
    def _create_lens(self, key: HierarchyUnambiguousKey, /) -> Hierarchy:
        return Hierarchy(
            HierarchyIdentifier.from_key(key),
            client=self._client,
            cube_identifier=self._cube_identifier,
        )

    @override
    def _get_unambiguous_keys(
        self,
        *,
        key: HierarchyKey | None,
    ) -> list[HierarchyUnambiguousKey]:
        dimension_name, hierarchy_name = (
            (None, None) if key is None else _normalize_key(key)
        )
        graphql_client = self._client._graphql_client

        # Remove `self._client._py4j_client is None` once `QuerySession`s are supported.
        if self._client._py4j_client is None or graphql_client is None:
            discovery = get_discovery(client=self._client)
            return [
                (dimension.name, hierarchy.name)
                for dimension in discovery.cubes[
                    self._cube_identifier.cube_name
                ].dimensions
                if dimension.name not in _RESERVED_DIMENSION_NAMES
                and (dimension_name is None or dimension.name == dimension_name)
                for hierarchy in dimension.hierarchies
                if hierarchy_name is None or hierarchy.name == hierarchy_name
            ]

        if hierarchy_name is None:
            output = graphql_client.get_hierarchies(
                cube_name=self._cube_identifier.cube_name
            )
            return [
                (dimension.name, hierarchy.name)
                for dimension in output.data_model.cube.dimensions
                if dimension.name not in _RESERVED_DIMENSION_NAMES
                for hierarchy in dimension.hierarchies
            ]

        if dimension_name is None:
            output = graphql_client.find_hierarchy_across_dimensions(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
                cube_name=self._cube_identifier.cube_name,
                hierarchy_name=hierarchy_name,
            )
            return [
                (dimension.name, dimension.hierarchy.name)  # type: ignore[attr-defined]
                for dimension in output.data_model.cube.dimensions
                if dimension.name not in _RESERVED_DIMENSION_NAMES
                and dimension.hierarchy  # type: ignore[attr-defined]
            ]

        output = graphql_client.find_hierarchy(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
            cube_name=self._cube_identifier.cube_name,
            dimension_name=dimension_name,
            hierarchy_name=hierarchy_name,
        )
        dimension = output.data_model.cube.dimension  # type: ignore[attr-defined]
        return (
            [HierarchyIdentifier._from_graphql(dimension.hierarchy).key]
            if dimension
            and dimension.hierarchy
            and dimension.hierarchy.dimension.name not in _RESERVED_DIMENSION_NAMES
            else []
        )

    @override
    def _update_delegate(  # noqa: C901, PLR0912
        self,
        other: Mapping[
            HierarchyKey,
            # `None` means delete the hierarchy at this key.
            _HierarchyConvertible | None,
        ],
        /,
    ) -> None:
        deleted: dict[DimensionName, set[HierarchyName]] = defaultdict(set)
        updated: dict[
            DimensionName,
            dict[HierarchyName, Mapping[LevelName, ColumnIdentifier | LevelIdentifier]],
        ] = defaultdict(
            dict,
        )

        for hierarchy_key, elements in other.items():
            dimension_name, hierarchy_name = _normalize_key(hierarchy_key)

            if elements is None:
                if dimension_name is None:
                    dimension_name = self[hierarchy_name].dimension

                deleted[dimension_name].add(hierarchy_name)
            else:
                mapping: dict[LevelName, ColumnIdentifier | LevelIdentifier] = {}

                if isinstance(elements, Sequence):
                    for element in elements:
                        match identify(element):
                            case ColumnIdentifier() as column_identifier:
                                mapping[column_identifier.column_name] = (
                                    column_identifier
                                )
                            case LevelIdentifier() as level_identifier:
                                mapping[level_identifier.level_name] = level_identifier
                else:
                    mapping = {
                        name: identify(value)  # type: ignore[misc]
                        for name, value in elements.items()
                    }

                del elements

                if dimension_name is None:
                    assert (hierarchy_name in self) is not None, (
                        f"Expected zero or one hierarchy named `{hierarchy_name}` across all dimensions."
                    )
                    dimension_name = _infer_dimension_name(next(iter(mapping.values())))

                updated[dimension_name][hierarchy_name] = mapping

        if deleted:
            py4j_client = self._client._require_py4j_client()

            py4j_client.update_hierarchies_for_cube(
                self._cube_identifier.cube_name,
                deleted=deleted,
                updated={
                    dimension_name: {
                        hierarchy_name: {
                            level_name: _get_column_identifier(
                                element,
                                client=self._client,
                                cube_identifier=self._cube_identifier,
                            )
                            for level_name, element in levels.items()
                        }
                        for hierarchy_name, levels in hierarchy.items()
                    }
                    for dimension_name, hierarchy in updated.items()
                },
            )
            py4j_client.refresh()
            return

        selection_field_from_identifier = _get_selection_field_from_identifier(
            updated, client=self._client, cube_identifier=self._cube_identifier
        )

        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for dimension_name, hierarchies in updated.items():
                for hierarchy_name, levels in hierarchies.items():
                    graphql_input = _get_create_hierarchy_input(
                        levels,
                        cube_identifier=self._cube_identifier,
                        identifier=HierarchyIdentifier.from_key(
                            (dimension_name, hierarchy_name)
                        ),
                        selection_field_from_identifier=selection_field_from_identifier,
                    )
                    graphql_client.create_hierarchy(input=graphql_input)

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[HierarchyKey], /) -> None:
        identifier_from_key: dict[HierarchyKey, HierarchyIdentifier] = {}
        for key in keys:
            match key:
                case dimension_name, hierarchy_name:
                    identifier_from_key[key] = HierarchyIdentifier.from_key(
                        (dimension_name, hierarchy_name)
                    )
                case _:
                    identifier_from_key[key] = self[key]._identifier

        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for key, identifier in identifier_from_key.items():
                graphql_input = DeleteHierarchyInput(
                    cube_name=self._cube_identifier.cube_name,
                    hierarchy_identifier=identifier._graphql_input,
                )
                graphql_client.delete_hierarchy(
                    input=graphql_input
                ).set_output_validator(
                    create_delete_status_validator(
                        key, lambda output: output.delete_hierarchy.status
                    )
                )

    @override
    def _repr_json_(self) -> ReprJson:
        dimensions: dict[DimensionName, list[Hierarchy]] = defaultdict(list)
        for hierarchy in self.values():
            dimensions[hierarchy.dimension].append(hierarchy)
        json = {
            dimension: dict(
                sorted(
                    {
                        hierarchy._repr_json_()[1]["root"]: hierarchy._repr_json_()[0]
                        for hierarchy in dimension_hierarchies
                    }.items(),
                ),
            )
            for dimension, dimension_hierarchies in sorted(dimensions.items())
        }
        return json, {"expanded": True, "root": "Dimensions"}
