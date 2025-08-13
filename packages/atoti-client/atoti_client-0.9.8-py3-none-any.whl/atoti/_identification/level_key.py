from typing import TypeAlias

from .dimension_name import DimensionName
from .hierarchy_name import HierarchyName
from .level_name import LevelName

LevelUnambiguousKey: TypeAlias = tuple[DimensionName, HierarchyName, LevelName]
LevelKey: TypeAlias = LevelName | tuple[HierarchyName, LevelName] | LevelUnambiguousKey


def normalize_level_key(  # type: ignore[return]
    key: LevelKey, /
) -> tuple[DimensionName | None, HierarchyName | None, LevelName]:
    match key:
        case str():
            return None, None, key
        case (hierarchy_name, level_name):
            return None, hierarchy_name, level_name
        case (_, _, _):
            return key  # type: ignore[return-value]


def java_description_from_level_key(key: LevelKey, /) -> str:  # type: ignore[return]
    match key:
        case str():
            return key
        case (hierarchy_name, level_name):
            return f"{level_name}@{hierarchy_name}"
        case (dimension_name, hierarchy_name, level_name):
            return f"{level_name}@{hierarchy_name}@{dimension_name}"


def level_key_from_java_description(java_description: str, /) -> LevelKey:
    parts = java_description.split("@")
    match parts:
        case [level_name]:
            return level_name
        case [level_name, hierarchy_name]:
            return (hierarchy_name, level_name)
        case [level_name, hierarchy_name, dimension_name]:
            return dimension_name, hierarchy_name, level_name
        case _:
            raise ValueError(
                f"Invalid java description for a level: {java_description}"
            )
