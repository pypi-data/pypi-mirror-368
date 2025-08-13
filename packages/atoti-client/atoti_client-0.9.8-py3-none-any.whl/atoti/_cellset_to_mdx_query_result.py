from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Collection, Mapping
from typing import TYPE_CHECKING, Any

import pandas as pd

from ._cellset import (
    CellSet,
    CellSetAxis,
    CellSetCellProperties,
    CellSetHierarchy,
    CellSetMember,
)
from ._column_definition import ColumnDefinition
from ._cube_discovery import Cube, DefaultMember
from ._data_type import DataType
from ._get_data_types import GetDataTypes
from ._identification import (
    MEASURES_HIERARCHY_IDENTIFIER,
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
)
from ._mdx_query import Context
from ._pandas import convert_series, create_dataframe
from .mdx_query_result import MdxQueryResult

if TYPE_CHECKING:
    # This requires pandas' optional dependency jinja2.
    from pandas.io.formats.style import Styler  # pylint: disable=nested-import


_MEASURES_HIERARCHY = CellSetHierarchy(
    dimension=MEASURES_HIERARCHY_IDENTIFIER.dimension_identifier.dimension_name,
    hierarchy=MEASURES_HIERARCHY_IDENTIFIER.hierarchy_name,
)

_GRAND_TOTAL_CAPTION = "Total"


def _is_slicer(axis: CellSetAxis, /) -> bool:
    return axis.id == -1


def _get_default_measure(
    default_members: Collection[DefaultMember],
    /,
) -> CellSetMember | None:
    return next(
        (
            CellSetMember(caption_path=member.caption_path, name_path=member.path)
            for member in default_members
            if member.dimension == _MEASURES_HIERARCHY.dimension
            and member.hierarchy == _MEASURES_HIERARCHY.hierarchy
        ),
        None,
    )


def _get_measure_names_and_captions(
    axes: Collection[CellSetAxis],
    /,
    *,
    default_measure: CellSetMember | None,
) -> tuple[list[str], list[str]]:
    if not axes:
        # When there are no axes at all, there is only one cell:
        # the value of the default measure aggregated at the top.
        return (
            ([default_measure.name_path[0]], [default_measure.caption_path[0]])
            if default_measure
            else ([], [])
        )

    # While looping on all the positions related to the Measures axis, the name of the same measure will come up repeatedly.
    # Only one occurrence of each measure name should be kept and the order of the occurrences must be preserved.
    name_to_caption = {
        position[hierarchy_index].name_path[0]: position[hierarchy_index].caption_path[
            0
        ]
        for axis in axes
        if not _is_slicer(axis)
        for hierarchy_index, hierarchy in enumerate(axis.hierarchies)
        if hierarchy == _MEASURES_HIERARCHY
        for position in axis.positions
    }

    return list(name_to_caption.keys()), list(name_to_caption.values())


def _get_level_identifiers(
    axes: Collection[CellSetAxis],
    /,
    *,
    cube: Cube,
) -> list[LevelIdentifier]:
    return [
        LevelIdentifier.from_key((hierarchy.dimension, hierarchy.hierarchy, level.name))
        for axis in axes
        if not _is_slicer(axis)
        for hierarchy_index, hierarchy in enumerate(axis.hierarchies)
        if hierarchy != _MEASURES_HIERARCHY
        for level_index, level in enumerate(
            cube.name_to_dimension[hierarchy.dimension]
            .name_to_hierarchy[hierarchy.hierarchy]
            .levels,
        )
        if level_index < axis.max_level_per_hierarchy[hierarchy_index]
        and level.type != "ALL"
    ]


# See https://docs.microsoft.com/en-us/analysis-services/multidimensional-models/mdx/mdx-cell-properties-fore-color-and-back-color-contents.
# Improved over from https://github.com/activeviam/atoti-ui/blob/bae9b2836ac58d6cb17f641656c89fdca36468cd/packages/data-visualization/src/getDataPointStyleFromProperties.ts#L5-L25.
def _cell_color_to_css_value(color: int | str, /) -> str:
    if isinstance(color, str):
        return "transparent" if color == '"transparent"' else color
    rest, red = divmod(color, 256)
    rest, green = divmod(rest, 256)
    rest, blue = divmod(rest, 256)
    return f"rgb({red}, {green}, {blue})"


# See https://docs.microsoft.com/en-us/analysis-services/multidimensional-models/mdx/mdx-cell-properties-using-cell-properties.
def _cell_font_flags_to_styles(font_flags: int, /) -> list[str]:
    styles = []
    text_decorations = []

    if font_flags & 1 == 1:
        styles.append("font-weight: bold")
    if font_flags & 2 == 2:  # noqa: PLR2004
        styles.append("font-style: italic")
    if font_flags & 4 == 4:  # noqa: PLR2004
        text_decorations.append("underline")
    if font_flags & 8 == 8:  # noqa: PLR2004
        text_decorations.append("line-through")

    if text_decorations:
        styles.append(f"""text-decoration: {" ".join(text_decorations)}""")

    return styles


def _cell_properties_to_style(properties: CellSetCellProperties, /) -> str:
    styles = []

    if properties.BACK_COLOR is not None:
        styles.append(
            f"background-color: {_cell_color_to_css_value(properties.BACK_COLOR)}",
        )

    if properties.FONT_FLAGS is not None:
        styles.extend(_cell_font_flags_to_styles(properties.FONT_FLAGS))

    if properties.FONT_NAME is not None:
        styles.append(f"font-family: {properties.FONT_NAME}")

    if properties.FONT_SIZE is not None:
        styles.append(f"font-size: {properties.FONT_SIZE}px")

    if properties.FORE_COLOR is not None:
        styles.append(f"color: {_cell_color_to_css_value(properties.FORE_COLOR)}")

    return "; ".join(styles)


CellMembers = dict[HierarchyIdentifier, CellSetMember]


def _get_cell_members_and_is_total(
    ordinal: int,
    /,
    *,
    axes: Collection[CellSetAxis],
    cube: Cube,
    keep_totals: bool,
) -> tuple[CellMembers, bool]:
    cell_members: CellMembers = {}
    is_total = False

    for axis in axes:
        if _is_slicer(axis):
            continue

        ordinal, position_index = divmod(ordinal, len(axis.positions))
        for hierarchy_index, hierarchy in enumerate(axis.hierarchies):
            hierarchy_identifier = HierarchyIdentifier.from_key(
                (hierarchy.dimension, hierarchy.hierarchy)
            )
            member = axis.positions[position_index][hierarchy_index]

            is_total |= (
                len(member.name_path) != axis.max_level_per_hierarchy[hierarchy_index]
            )

            if not keep_totals and is_total:
                return {}, True

            cell_members[hierarchy_identifier] = (
                member
                if hierarchy_identifier == MEASURES_HIERARCHY_IDENTIFIER
                or cube.name_to_dimension[
                    hierarchy_identifier.dimension_identifier.dimension_name
                ]
                .name_to_hierarchy[hierarchy_identifier.hierarchy_name]
                .slicing
                else CellSetMember(
                    caption_path=member.caption_path[1:],
                    name_path=member.name_path[1:],
                )
            )

    return cell_members, is_total


def _get_member_name_index(
    level_identifiers: Collection[LevelIdentifier],
    /,
    *,
    cube_name: str,
    get_data_types: GetDataTypes | None,
    keep_totals: bool,
    members: Collection[tuple[str | None, ...]],
) -> pd.Index[Any] | None:
    if not level_identifiers:
        return None

    data_types: dict[LevelIdentifier, DataType] = (
        get_data_types(level_identifiers, cube_name=cube_name)
        if get_data_types
        else dict.fromkeys(level_identifiers, "Object")
    )
    index_dataframe = create_dataframe(
        members,
        [
            ColumnDefinition(
                name=level_identifier.level_name,
                data_type=data_types[level_identifier],
                nullable=keep_totals,  # A level cell can only be null if it is a total.
            )
            for level_identifier in level_identifiers
        ],
    )

    return (
        pd.Index(index_dataframe.iloc[:, 0])
        if len(level_identifiers) == 1
        else pd.MultiIndex.from_frame(index_dataframe)
    )


def _get_member_caption_index(
    level_identifiers: Collection[LevelIdentifier],
    /,
    *,
    cube: Cube,
    members: Collection[tuple[str | None, ...]],
) -> pd.Index[Any] | None:
    if not level_identifiers:
        return None

    level_captions = tuple(
        next(
            level.caption
            for level in cube.name_to_dimension[
                level_identifier.hierarchy_identifier.dimension_identifier.dimension_name
            ]
            .name_to_hierarchy[level_identifier.hierarchy_identifier.hierarchy_name]
            .levels
            if level.name == level_identifier.level_name
        )
        for level_identifier in level_identifiers
    )

    members_with_grand_total_caption = (
        (_GRAND_TOTAL_CAPTION,)
        if all(element is None for element in member)
        else member
        for member in members
    )

    index_dataframe = pd.DataFrame(
        members_with_grand_total_caption,
        columns=level_captions,
        dtype="string",
    ).fillna("")

    if len(level_identifiers) == 1:
        return pd.Index(index_dataframe.iloc[:, 0])  # type: ignore[no-any-return]

    return pd.MultiIndex.from_frame(index_dataframe)


# See https://activeviam.atlassian.net/browse/PYTHON-370.
def _convert_measure_series(
    series: pd.Series[Any],
    /,
    *,
    data_type: DataType,
) -> pd.Series[Any]:
    try:
        return convert_series(
            series,
            data_type=data_type,
            nullable=True,  # Measure values are always nullable.
        )
    except ValueError:
        return series


def _get_measure_values(
    measure_values: Collection[Mapping[str, object]],
    /,
    *,
    cube_name: str,
    get_data_types: GetDataTypes | None,
    index: pd.Index[Any] | None,
    measure_names: Collection[str],
) -> dict[str, Collection[object]]:
    types: dict[MeasureIdentifier, DataType] = (
        get_data_types(
            [MeasureIdentifier(measure_name) for measure_name in measure_names],
            cube_name=cube_name,
        )
        if get_data_types
        else {
            MeasureIdentifier(measure_name): "Object" for measure_name in measure_names
        }
    )

    return {
        measure_name: _convert_measure_series(
            pd.Series(
                [values.get(measure_name) for values in measure_values],
                dtype="object",  # To prevent any preliminary conversion.
                index=index,
            ),
            data_type=types[MeasureIdentifier(measure_name)],
        )
        for measure_name in measure_names
    }


def cellset_to_mdx_query_result(
    cellset: CellSet,
    /,
    *,
    context: Context | None = None,
    cube: Cube,
    get_data_types: GetDataTypes | None = None,
    keep_totals: bool,
) -> MdxQueryResult:
    assert cellset.cube == cube.name

    default_measure = _get_default_measure(cellset.default_members)

    has_some_style = not all(cell.properties.is_empty for cell in cellset.cells)

    member_captions_to_measure_formatted_values: dict[
        tuple[str | None, ...],
        dict[str, str],
    ] = defaultdict(dict)
    member_captions_to_measure_styles: dict[
        tuple[str | None, ...],
        dict[str, str],
    ] = defaultdict(dict)
    member_names_to_measure_values: dict[
        tuple[str | None, ...],
        dict[str, object],
    ] = defaultdict(dict)

    has_some_cells_or_any_non_measures_hierarchy = cellset.cells or any(
        hierarchy != _MEASURES_HIERARCHY
        for axis in cellset.axes
        for hierarchy in axis.hierarchies
    )
    cell_count = (
        # The received cell set is sparse (i.e. empty cells are omitted) so it is important to loop over all the possible ordinals.
        math.prod([len(axis.positions) for axis in cellset.axes])
        if has_some_cells_or_any_non_measures_hierarchy
        else 0
    )

    for ordinal in range(cell_count):
        cell = cellset.ordinal_to_cell.get(ordinal)

        cell_members, is_total = _get_cell_members_and_is_total(
            ordinal,
            axes=cellset.axes,
            cube=cube,
            keep_totals=keep_totals,
        )

        if keep_totals or not is_total:
            if not default_measure:
                raise RuntimeError(
                    "Expected a default member for measures but found none.",
                )

            measure = cell_members.setdefault(
                MEASURES_HIERARCHY_IDENTIFIER,
                default_measure,
            )

            non_measure_cell_members = tuple(
                cell_member
                for hierarchy, cell_member in cell_members.items()
                if hierarchy != MEASURES_HIERARCHY_IDENTIFIER
            )

            member_names: tuple[str | None, ...] = tuple(
                name
                for member in non_measure_cell_members
                for name in member.name_path
                # Replacing empty collection with `None` so that the member is still taken into account.
                or [None]  # type: ignore[list-item]
            )
            member_captions: tuple[str | None, ...] = tuple(
                name
                for member in non_measure_cell_members
                for name in member.caption_path
                # Replacing empty collection with `None` so that the member is still taken into account.
                or [None]  # type: ignore[list-item]
            )

            member_names_to_measure_values[member_names][measure.name_path[0]] = (
                None if cell is None else cell.value
            )
            member_captions_to_measure_formatted_values[member_captions][
                measure.caption_path[0]
            ] = "" if cell is None else cell.pythonic_formatted_value

            if has_some_style:
                member_captions_to_measure_styles[member_captions][
                    measure.caption_path[0]
                ] = "" if cell is None else _cell_properties_to_style(cell.properties)

    level_identifiers = _get_level_identifiers(
        cellset.axes,
        cube=cube,
    )

    member_name_index = _get_member_name_index(
        level_identifiers,
        cube_name=cellset.cube,
        get_data_types=get_data_types,
        keep_totals=keep_totals,
        members=member_names_to_measure_values.keys(),
    )

    member_caption_index = _get_member_caption_index(
        level_identifiers,
        cube=cube,
        members=member_captions_to_measure_formatted_values.keys(),
    )

    measure_names, measure_captions = _get_measure_names_and_captions(
        cellset.axes,
        default_measure=default_measure,
    )

    formatted_values_dataframe = pd.DataFrame(
        member_captions_to_measure_formatted_values.values(),
        columns=measure_captions,
        dtype="string",
        index=member_caption_index,
    ).fillna("")

    def _get_styler() -> Styler:
        styler = formatted_values_dataframe.style

        if has_some_style:

            def apply_style(_: pd.DataFrame) -> pd.DataFrame:
                return pd.DataFrame(
                    member_captions_to_measure_styles.values(),
                    dtype="string",
                    columns=measure_captions,
                    index=member_caption_index,
                )

            styler = styler.apply(apply_style, axis=None)

        return styler

    measure_values = _get_measure_values(
        member_names_to_measure_values.values(),
        cube_name=cellset.cube,
        get_data_types=get_data_types,
        index=member_name_index,
        measure_names=measure_names,
    )

    # `pandas-stub` declares a `__new__` but `pandas` actually have an `__init__`.
    return MdxQueryResult(  # pyright: ignore[reportCallIssue]
        measure_values,
        context=context,
        formatted_values=formatted_values_dataframe,
        get_styler=_get_styler,
        index=member_name_index,
    )
