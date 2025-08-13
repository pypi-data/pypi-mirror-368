from __future__ import annotations

from collections.abc import Collection
from dataclasses import asdict
from functools import cached_property
from typing import Annotated, final

from pydantic import ConfigDict, PlainSerializer
from pydantic.dataclasses import dataclass

from ._collections import FrozenSequence, frozendict
from ._cube_discovery import DefaultMember
from ._pydantic import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    create_camel_case_alias_generator,
)

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


_PYDANTIC_CONFIG_WITH_ALIAS: ConfigDict = {
    **_PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(),
}


@final
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True, kw_only=True)
class CellSetHierarchy:
    dimension: str
    hierarchy: str


@final
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True, kw_only=True)
class CellSetMember:
    caption_path: FrozenSequence[str]
    name_path: FrozenSequence[str]


@final
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True, kw_only=True)
class CellSetAxis:
    hierarchies: FrozenSequence[CellSetHierarchy]
    id: int
    positions: FrozenSequence[FrozenSequence[CellSetMember]]

    @cached_property
    def max_level_per_hierarchy(self) -> tuple[int, ...]:
        """This property always existed in cell sets returned by the WebSocket API but was only added to those returned by the HTTP API in Atoti Server 6.0.9.

        Using it helps keeping the logic to convert a cell set to a table similar to the one used by Atoti UI.
        """
        return tuple(
            max(
                (
                    len(position[hierarchy_index].name_path)
                    for position in self.positions
                ),
                default=0,
            )
            for hierarchy_index in range(len(self.hierarchies))
        )


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class CellSetCellProperties:
    BACK_COLOR: int | str | None = None
    FONT_FLAGS: int | None = None
    FONT_NAME: str | None = None
    FONT_SIZE: int | None = None
    FORE_COLOR: int | str | None = None

    @cached_property
    def is_empty(self, /) -> bool:
        return all(value is None for value in asdict(self).values())


@final
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True, kw_only=True)
class CellSetCell:
    ordinal: int
    properties: CellSetCellProperties
    value: object = None
    formatted_value: str | None = None

    @cached_property
    def pythonic_formatted_value(self) -> str:
        return (
            str(self.value)
            if isinstance(self.value, bool) or self.formatted_value is None
            else self.formatted_value
        )


def _sort_cells(cells: Collection[CellSetCell], /) -> list[CellSetCell]:
    return sorted(cells, key=lambda cell: cell.ordinal)


@final
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True, kw_only=True)
class CellSet:
    axes: FrozenSequence[CellSetAxis]
    cells: Annotated[
        FrozenSequence[CellSetCell],
        # To keep snapshots stable.
        PlainSerializer(_sort_cells, when_used="json"),
    ]
    cube: str
    default_members: FrozenSequence[DefaultMember]

    @cached_property
    def ordinal_to_cell(self) -> frozendict[int, CellSetCell]:
        return frozendict({cell.ordinal: cell for cell in self.cells})
