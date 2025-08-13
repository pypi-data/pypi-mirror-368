from __future__ import annotations

from collections.abc import Sequence
from functools import cached_property
from typing import Annotated, final

from pydantic import AfterValidator, ConfigDict
from pydantic.dataclasses import dataclass

from .._collections import FrozenSequence, frozendict
from .._identification import DimensionName, HierarchyName, LevelName, MeasureName
from .._pydantic import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    create_camel_case_alias_generator,
)

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Level:
    caption: str
    name: LevelName
    type: str


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Hierarchy:
    caption: str
    folder: str | None = None
    levels: FrozenSequence[Level]
    name: HierarchyName
    slicing: bool
    visible: bool

    @cached_property
    def name_to_level(self) -> frozendict[HierarchyName, Level]:
        return frozendict({level.name: level for level in self.levels})


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Dimension:
    caption: str
    default_hierarchy: HierarchyName
    hierarchies: FrozenSequence[Hierarchy]
    name: DimensionName
    type: str

    @cached_property
    def name_to_hierarchy(self) -> frozendict[DimensionName, Hierarchy]:
        return frozendict({hierarchy.name: hierarchy for hierarchy in self.hierarchies})


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Measure:
    caption: str
    description: str | None = None
    folder: str | None = None
    format_string: str | None = None
    name: MeasureName
    visible: bool


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class DefaultMember:
    caption_path: FrozenSequence[str]
    dimension: DimensionName
    hierarchy: HierarchyName
    path: FrozenSequence[str]


def _sort_measures(measures: Sequence[Measure], /) -> tuple[Measure, ...]:
    """Sort measures by name to ensure snapshot stability."""
    return tuple(sorted(measures, key=lambda measure: measure.name))


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Cube:
    default_members: FrozenSequence[DefaultMember]
    dimensions: FrozenSequence[Dimension]
    measures: Annotated[
        FrozenSequence[Measure],
        AfterValidator(_sort_measures),
    ]
    name: str

    @cached_property
    def name_to_dimension(self) -> frozendict[DimensionName, Dimension]:
        return frozendict({dimension.name: dimension for dimension in self.dimensions})

    @cached_property
    def name_to_measure(self) -> frozendict[MeasureName, Measure]:
        return frozendict({measure.name: measure for measure in self.measures})


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Catalog:
    cubes: FrozenSequence[Cube]
    name: str

    @cached_property
    def name_to_cube(self) -> frozendict[str, Cube]:
        return frozendict({cube.name: cube for cube in self.cubes})


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Discovery:
    catalogs: FrozenSequence[Catalog]

    @cached_property
    def cubes(self) -> frozendict[str, Cube]:
        return frozendict(
            # Cubes can be part of multiple catalogs.
            # If two catalogs have a cube with the same name, it is the same cube.
            {cube.name: cube for catalog in self.catalogs for cube in catalog.cubes},
        )
