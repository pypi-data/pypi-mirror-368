from collections.abc import Set as AbstractSet

from ._identification import (
    HierarchyIdentifier,
    Identifiable,
    LevelIdentifier,
    LevelName,
    identify,
)


def validate_hierarchy_unicity(
    levels: AbstractSet[Identifiable[LevelIdentifier]],
    /,
) -> AbstractSet[LevelIdentifier]:
    levels_grouped_by_hierarchy: dict[HierarchyIdentifier, LevelName] = {}

    for level in levels:
        level_identifier = identify(level)
        existing_level_name = levels_grouped_by_hierarchy.get(
            level_identifier.hierarchy_identifier
        )
        if existing_level_name is not None:
            raise ValueError(
                f"The passed levels must belong to different hierarchies but levels `{existing_level_name}` and `{level_identifier.level_name}` were given for `{level_identifier.hierarchy_identifier}`."
            )
        levels_grouped_by_hierarchy[level_identifier.hierarchy_identifier] = (
            level_identifier.level_name
        )

    return frozenset(
        LevelIdentifier(hierarchy_identifier, level_name)
        for hierarchy_identifier, level_name in levels_grouped_by_hierarchy.items()
    )
