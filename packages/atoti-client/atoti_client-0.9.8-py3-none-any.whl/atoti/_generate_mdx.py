from __future__ import annotations

from collections.abc import Mapping, Sequence, Set as AbstractSet
from dataclasses import dataclass, replace
from functools import reduce
from typing import Literal, final

from ._constant import Constant, Scalar, json_from_constant, str_from_scalar
from ._cube_discovery import Cube
from ._cube_query_filter_condition import (
    CubeQueryFilterCondition,
    _CubeQueryFilterIsInLevelCondition,
    _CubeQueryFilterIsInMeasureCondition,
    _CubeQueryFilterLeafCondition,
    _CubeQueryFilterRelationalLevelCondition,
    _CubeQueryFilterRelationalMeasureCondition,
)
from ._identification import (
    EPOCH_HIERARCHY_IDENTIFIER,
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
)
from ._mdx_ast import (
    ColumnsAxisName,
    MdxAxis,
    MdxCompoundIdentifier,
    MdxExpression,
    MdxFromClause,
    MdxFunction,
    MdxHierarchyCompoundIdentifier,
    MdxLevelCompoundIdentifier,
    MdxLiteral,
    MdxMeasureCompoundIdentifier,
    MdxMemberCompoundIdentifier,
    MdxSelect,
    MdxSubSelect,
    MdxUndefinedCompoundIdentifier,
    RegularAxisName,
    RowsAxisName,
    SlicerAxisName,
)
from ._operation import (
    HierarchyMembershipCondition,
    MembershipCondition,
    RelationalCondition,
    RelationalOperator,
    dnf_from_condition,
)


def _generate_columns_axis(
    measure_identifiers: Sequence[MeasureIdentifier],
    /,
    *,
    measure_conditions: Sequence[
        _CubeQueryFilterRelationalMeasureCondition
        | _CubeQueryFilterIsInMeasureCondition
    ],
) -> MdxAxis[ColumnsAxisName]:
    return MdxAxis(
        expression=_add_measure_filter(
            MdxFunction.braces(
                [
                    MdxMeasureCompoundIdentifier.of(measure_identifier)
                    for measure_identifier in measure_identifiers
                ],
            ),
            measure_conditions,
        ),
        name="COLUMNS",
    )


def _keep_only_deepest_levels(
    level_identifiers: Sequence[LevelIdentifier],
    /,
    *,
    cube: Cube,
) -> dict[LevelIdentifier, int]:
    hierarchy_to_max_level_depth: dict[HierarchyIdentifier, int] = {}

    for level_identifier in level_identifiers:
        hierarchy_identifier = level_identifier.hierarchy_identifier
        current_max_level_depth = hierarchy_to_max_level_depth.get(
            hierarchy_identifier,
            -1,
        )
        level_depth = next(
            level_index
            for level_index, level in enumerate(
                cube.name_to_dimension[
                    hierarchy_identifier.dimension_identifier.dimension_name
                ]
                .name_to_hierarchy[hierarchy_identifier.hierarchy_name]
                .levels,
            )
            if level.name == level_identifier.level_name
        )

        if level_depth > current_max_level_depth:
            hierarchy_to_max_level_depth[hierarchy_identifier] = level_depth

    return {
        LevelIdentifier(
            hierarchy_identifier,
            cube.name_to_dimension[
                hierarchy_identifier.dimension_identifier.dimension_name
            ]
            .name_to_hierarchy[hierarchy_identifier.hierarchy_name]
            .levels[depth]
            .name,
        ): depth
        for hierarchy_identifier, depth in hierarchy_to_max_level_depth.items()
    }


def _generate_level_expression(
    level_identifier: LevelIdentifier,
    /,
    *,
    cube: Cube,
    include_totals: bool,
    level_depth: int,
) -> MdxExpression:
    hierarchy = cube.name_to_dimension[
        level_identifier.hierarchy_identifier.dimension_identifier.dimension_name
    ].name_to_hierarchy[level_identifier.hierarchy_identifier.hierarchy_name]

    if not include_totals:
        return MdxFunction.property(
            "Members",
            MdxLevelCompoundIdentifier.of(level_identifier),
        )

    if hierarchy.slicing:
        first_level_identifier = LevelIdentifier(
            level_identifier.hierarchy_identifier,
            hierarchy.levels[0].name,
        )
        member_expression = MdxFunction.property(
            "Members",
            MdxLevelCompoundIdentifier.of(first_level_identifier),
        )
    else:
        member_expression = MdxFunction.braces(
            [
                MdxMemberCompoundIdentifier.of(
                    "AllMember",
                    level_identifier=LevelIdentifier(
                        level_identifier.hierarchy_identifier,
                        hierarchy.levels[0].name,
                    ),
                    hierarchy_first_level_name=hierarchy.levels[0].name,
                ),
            ],
        )

    if level_depth == 0:
        return member_expression

    return MdxFunction.function(
        "Hierarchize",
        [
            MdxFunction.function(
                "Descendants",
                [
                    member_expression,
                    MdxLiteral.scalar(str(level_depth)),
                    MdxLiteral.keyword("SELF_AND_BEFORE"),
                ],
            ),
        ],
    )


def _generate_rows_axis(
    level_identifiers: Mapping[LevelIdentifier, int],
    /,
    *,
    cube: Cube,
    include_totals: bool,
    measure_conditions: Sequence[
        _CubeQueryFilterRelationalMeasureCondition
        | _CubeQueryFilterIsInMeasureCondition
    ],
    non_empty: bool,
) -> MdxAxis[RowsAxisName]:
    expression: MdxExpression

    if len(level_identifiers) == 1:
        level_identifier, level_depth = next(iter(level_identifiers.items()))
        expression = _generate_level_expression(
            level_identifier,
            cube=cube,
            include_totals=include_totals,
            level_depth=level_depth,
        )
    else:
        expression = MdxFunction.function(
            "Crossjoin",
            [
                _generate_level_expression(
                    level_identifier,
                    cube=cube,
                    include_totals=include_totals,
                    level_depth=level_depth,
                )
                for level_identifier, level_depth in level_identifiers.items()
            ],
        )

    expression = _add_measure_filter(expression, measure_conditions)

    # Adapted from https://github.com/activeviam/atoti-ui/blob/fd835ae09f2505d5a88a4068208013c092329e55/packages/mdx/src/ensureChildrenCardinalityInMemberProperties.tsx#L18.
    multi_level_hierarchy_identifiers = {
        HierarchyIdentifier.from_key((dimension.name, hierarchy.name))
        for dimension in cube.dimensions
        for hierarchy in dimension.hierarchies
        if len(hierarchy.levels) > (1 if hierarchy.slicing else 2)
    }
    has_at_least_one_multi_level_hierarchy = any(
        level_identifier.hierarchy_identifier in multi_level_hierarchy_identifiers
        for level_identifier in level_identifiers
    )
    properties = (
        (MdxLiteral.keyword("CHILDREN_CARDINALITY"),)
        if has_at_least_one_multi_level_hierarchy
        else ()
    )

    return MdxAxis(
        expression=expression,
        name="ROWS",
        non_empty=non_empty,
        properties=properties,
    )


def _is_hierarchy_shallowest_level(
    level_identifier: LevelIdentifier, /, *, cube: Cube
) -> bool:
    shallowest_level = next(
        level
        for level in cube.name_to_dimension[
            level_identifier.hierarchy_identifier.dimension_identifier.dimension_name
        ]
        .name_to_hierarchy[level_identifier.hierarchy_identifier.hierarchy_name]
        .levels
        if level.type != "ALL"
    )
    return level_identifier.level_name == shallowest_level.name


@final
@dataclass(frozen=True, kw_only=True)
class _HierarchyFilter:
    exclusion: bool
    members_or_member_paths: AbstractSet[Scalar | tuple[Scalar, ...]]

    def __and__(self, other: _HierarchyFilter, /) -> _HierarchyFilter:
        if not (self.exclusion and other.exclusion):
            raise ValueError("Only exclusion filters can be combined.")

        return _HierarchyFilter(
            exclusion=True,
            members_or_member_paths=self.members_or_member_paths
            | other.members_or_member_paths,
        )


def _process_conditions(  # noqa: C901, PLR0912
    conditions: Sequence[_CubeQueryFilterLeafCondition],
    /,
    *,
    cube: Cube,
    scenario_name: str | None,
) -> tuple[
    dict[HierarchyIdentifier, _HierarchyFilter],
    list[_CubeQueryFilterRelationalLevelCondition | _CubeQueryFilterIsInLevelCondition],
    list[
        _CubeQueryFilterRelationalMeasureCondition
        | _CubeQueryFilterIsInMeasureCondition
    ],
]:
    hierarchy_identifier_to_filter: dict[HierarchyIdentifier, _HierarchyFilter] = {}
    deep_level_conditions: list[
        _CubeQueryFilterRelationalLevelCondition | _CubeQueryFilterIsInLevelCondition
    ] = []
    measure_conditions: list[
        _CubeQueryFilterRelationalMeasureCondition
        | _CubeQueryFilterIsInMeasureCondition
    ] = []

    def add_hierarchy_filter(
        hierarchy_filter: _HierarchyFilter,
        /,
        *,
        hierarchy_identifier: HierarchyIdentifier,
    ) -> None:
        existing_filter = hierarchy_identifier_to_filter.get(hierarchy_identifier)

        hierarchy_identifier_to_filter[hierarchy_identifier] = (
            existing_filter & hierarchy_filter if existing_filter else hierarchy_filter
        )

    for condition in conditions:
        match condition:
            case HierarchyMembershipCondition(
                operator="in",  # `IS_NOT_IN` is not supported.
            ):
                add_hierarchy_filter(
                    _HierarchyFilter(
                        exclusion=False,
                        members_or_member_paths=condition.member_paths,
                    ),
                    hierarchy_identifier=condition.subject,
                )
            case MembershipCondition(subject=HierarchyIdentifier()):
                add_hierarchy_filter(
                    _HierarchyFilter(
                        exclusion=condition.operator == "not in",
                        members_or_member_paths=condition.elements,  # type: ignore[arg-type]
                    ),
                    hierarchy_identifier=condition.subject,  # type: ignore[arg-type]
                )
            case MembershipCondition(subject=LevelIdentifier()):
                if _is_hierarchy_shallowest_level(condition.subject, cube=cube):  # type: ignore[arg-type]
                    add_hierarchy_filter(
                        _HierarchyFilter(
                            exclusion=condition.operator == "not in",
                            members_or_member_paths={
                                (member,)  # type: ignore[misc]
                                for member in condition.elements
                            },
                        ),
                        hierarchy_identifier=condition.subject.hierarchy_identifier,  # type: ignore[union-attr]
                    )
                else:
                    deep_level_conditions.append(condition)  # type: ignore[arg-type]
            case MembershipCondition(subject=MeasureIdentifier()):
                measure_conditions.append(condition)  # type: ignore[arg-type]
            case RelationalCondition(
                subject=HierarchyIdentifier(),
                operator="==" | "!=",
            ):
                add_hierarchy_filter(
                    _HierarchyFilter(
                        exclusion=condition.operator == "!=",
                        members_or_member_paths={condition.target},  # type: ignore[arg-type]
                    ),
                    hierarchy_identifier=condition.subject,  # type: ignore[arg-type]
                )
            case RelationalCondition(subject=LevelIdentifier()):
                if _is_hierarchy_shallowest_level(condition.subject, cube=cube) and (  # type: ignore[arg-type]
                    condition.operator == "==" or condition.operator == "!="
                ):
                    add_hierarchy_filter(
                        _HierarchyFilter(
                            exclusion=condition.operator == "!=",
                            members_or_member_paths={(condition.target,)},  # type: ignore[arg-type]
                        ),
                        hierarchy_identifier=condition.subject.hierarchy_identifier,  # type: ignore[union-attr]
                    )
                else:
                    deep_level_conditions.append(condition)  # type: ignore[arg-type]
            case RelationalCondition(subject=MeasureIdentifier()):
                measure_conditions.append(condition)  # type: ignore[arg-type]

    if scenario_name is not None:
        hierarchy_identifier_to_filter[EPOCH_HIERARCHY_IDENTIFIER] = _HierarchyFilter(
            exclusion=False,
            members_or_member_paths={(scenario_name,)},
        )

    return hierarchy_identifier_to_filter, deep_level_conditions, measure_conditions


def _get_mdx_operator(relational_operator: RelationalOperator, /) -> str:
    match relational_operator:
        case "==":
            return "="
        case "!=":
            return "<>"
        case "<" | "<=" | ">" | ">=":
            return relational_operator


def _mdx_literal_from_constant(value: Constant, /) -> MdxLiteral:
    json_value = json_from_constant(value)

    match json_value:
        case bool():
            return MdxLiteral.scalar("TRUE" if json_value else "FALSE")
        case float() | int():
            return MdxLiteral.scalar(str(json_value))
        case str():
            return MdxLiteral.string(json_value)
        case _:
            raise TypeError(f"Unsupported constant: `{value}`.")


def _generate_level_filter_expression(
    condition: _CubeQueryFilterRelationalLevelCondition
    | _CubeQueryFilterIsInLevelCondition,
    /,
) -> MdxExpression:
    current_member_name_expression = MdxFunction.property(
        "MEMBER_VALUE",
        MdxFunction.property(
            "CurrentMember",
            MdxHierarchyCompoundIdentifier.of(condition.subject.hierarchy_identifier),
        ),
    )
    logical_expression: MdxExpression

    match condition:
        case RelationalCondition(operator=operator, target=target):
            logical_expression = MdxFunction.infix(
                _get_mdx_operator(operator),
                [
                    current_member_name_expression,
                    _mdx_literal_from_constant(target),
                ],
            )
        case MembershipCondition(operator=operator):
            match operator:
                case "in":
                    mdx_operator: str = "OR"
                    relational_operator: RelationalOperator = "=="
                case "not in":
                    mdx_operator = "AND"
                    relational_operator = "!="

            logical_expression = MdxFunction.infix(
                mdx_operator,
                [
                    MdxFunction.infix(
                        _get_mdx_operator(relational_operator),
                        [
                            current_member_name_expression,
                            _mdx_literal_from_constant(element),
                        ],
                    )
                    for element in condition._sorted_elements
                ],
            )

    return MdxFunction.function(
        "Filter",
        [
            MdxFunction.property(
                "Members",
                MdxLevelCompoundIdentifier.of(condition.subject),
            ),
            logical_expression,
        ],
    )


def _generate_compound_identifier_for_member_or_member_path(
    member_or_member_path: Scalar | tuple[Scalar, ...],
    /,
    *,
    cube: Cube,
    hierarchy_identifier: HierarchyIdentifier,
) -> MdxUndefinedCompoundIdentifier | MdxMemberCompoundIdentifier:
    if isinstance(member_or_member_path, tuple):
        hierarchy = cube.name_to_dimension[
            hierarchy_identifier.dimension_identifier.dimension_name
        ].name_to_hierarchy[hierarchy_identifier.hierarchy_name]
        level_index = (
            len(member_or_member_path) - 1
            if hierarchy.slicing
            else len(member_or_member_path)
        )
        return MdxMemberCompoundIdentifier.of(
            *([] if hierarchy.slicing else ["AllMember"]),
            *(str_from_scalar(member) for member in member_or_member_path),
            level_identifier=LevelIdentifier(
                hierarchy_identifier,
                level_name=hierarchy.levels[level_index].name,
            ),
            hierarchy_first_level_name=hierarchy.levels[0].name,
        )

    return MdxUndefinedCompoundIdentifier.of(
        hierarchy_identifier.dimension_identifier.dimension_name,
        hierarchy_identifier.hierarchy_name,
        str_from_scalar(member_or_member_path),
    )


_FilterClass = Literal["slicer", "sub_select"]


def _generate_except_function_for_member_in_unknown_level_of_hierarchy(
    compound_identifier: MdxCompoundIdentifier, /
) -> MdxFunction:
    return MdxFunction.function(
        "Except",
        [
            MdxFunction.property(
                "Members",
                MdxFunction.property("Level", compound_identifier),
            ),
            compound_identifier,
        ],
    )


# Adapted from https://github.com/activeviam/atoti-ui/blob/cf8f9aa102ab8eaa88ac1e11f036d56b2e4ca7b6/packages/mdx/src/internal/_getFilterClasses.ts.
def _generate_hierarchy_filter_expressions_and_class(
    hierarchy_filter: _HierarchyFilter,
    /,
    *,
    cube: Cube,
    hierarchy_identifier: HierarchyIdentifier,
    hierarchy_on_regular_axis: bool,
) -> tuple[tuple[MdxExpression, ...], _FilterClass]:
    compound_identifiers = [
        _generate_compound_identifier_for_member_or_member_path(
            member_or_member_path,
            cube=cube,
            hierarchy_identifier=hierarchy_identifier,
        )
        for member_or_member_path in sorted(hierarchy_filter.members_or_member_paths)
    ]

    expressions: tuple[MdxExpression, ...] = (
        (
            compound_identifiers[0]
            if len(compound_identifiers) == 1
            else MdxFunction.braces(compound_identifiers)
        ),
    )

    filter_class: _FilterClass = "sub_select"

    if hierarchy_filter.exclusion:
        member_in_unknown_level_of_hierarchy_compound_identifiers = [
            compound_identifier
            for compound_identifier in compound_identifiers
            if isinstance(compound_identifier, MdxUndefinedCompoundIdentifier)
        ]
        if len(member_in_unknown_level_of_hierarchy_compound_identifiers) == len(
            compound_identifiers
        ):
            expressions = tuple(
                _generate_except_function_for_member_in_unknown_level_of_hierarchy(
                    compound_identifier
                )
                for compound_identifier in member_in_unknown_level_of_hierarchy_compound_identifiers
            )
        else:
            expressions = tuple(
                MdxFunction.function(
                    "Except",
                    [
                        MdxFunction.property(
                            "Members",
                            MdxHierarchyCompoundIdentifier.of(hierarchy_identifier),
                        ),
                        expression,
                    ],
                )
                for expression in expressions
            )
    elif (
        not hierarchy_on_regular_axis
        and len(hierarchy_filter.members_or_member_paths) == 1
    ):
        filter_class = "slicer"

    return expressions, filter_class


def _create_slicer_axis(
    slicer_expressions: Sequence[MdxExpression],
    /,
) -> MdxAxis[SlicerAxisName] | None:
    if not slicer_expressions:
        return None

    return MdxAxis(
        expression=slicer_expressions[0]
        if len(slicer_expressions) == 1
        else MdxFunction.parentheses(slicer_expressions),
        name="SLICER",
    )


def _generate_multi_sub_select(
    filter_expressions: Sequence[MdxExpression],
    /,
    *,
    from_clause: MdxSubSelect | MdxFromClause,
    slicer_expressions: Sequence[MdxExpression],
) -> MdxSubSelect | MdxFromClause:
    match filter_expressions:
        case head, *tail:
            return MdxSubSelect(
                axes=[MdxAxis(expression=head, name="COLUMNS")],
                from_clause=_generate_multi_sub_select(
                    tail,
                    from_clause=from_clause,
                    slicer_expressions=slicer_expressions,
                ),
                slicer_axis=_create_slicer_axis(slicer_expressions),
            )
        case _:
            return from_clause


# Adapted from https://github.com/activeviam/atoti-ui/blob/cf8f9aa102ab8eaa88ac1e11f036d56b2e4ca7b6/packages/mdx/src/internal/_setFiltersWithClasses.ts.
def _add_hierarchy_filters(
    select: MdxSelect,
    filter_class_from_expressions: Mapping[tuple[MdxExpression, ...], _FilterClass],
    /,
) -> MdxSelect:
    slicer_expressions: list[MdxExpression] = []

    for filter_expressions, filter_class in filter_class_from_expressions.items():
        match filter_class:
            case "slicer":
                slicer_expressions.extend(filter_expressions)
            case "sub_select":
                select = replace(
                    select,
                    from_clause=_generate_multi_sub_select(
                        filter_expressions,
                        from_clause=select.from_clause,
                        slicer_expressions=slicer_expressions,
                    ),
                )

    return replace(
        select,
        slicer_axis=_create_slicer_axis(slicer_expressions),
    )


def _generate_measure_filter_exression(
    condition: _CubeQueryFilterRelationalMeasureCondition
    | _CubeQueryFilterIsInMeasureCondition,
    /,
) -> MdxExpression:
    match condition:
        case RelationalCondition(subject=subject, operator=operator, target=target):
            identifier = MdxMeasureCompoundIdentifier.of(subject)
            return (
                MdxFunction.function("IsNull", [identifier])
                if target is None
                else MdxFunction.infix(
                    _get_mdx_operator(operator),
                    [identifier, _mdx_literal_from_constant(target)],
                )
            )
        case MembershipCondition(subject=subject, operator=operator):
            match operator:
                case "in":
                    mdx_operator: str = "OR"
                    relational_operator: RelationalOperator = "=="
                case "not in":
                    mdx_operator = "AND"
                    relational_operator = "!="
            expressions = [
                _generate_measure_filter_exression(
                    RelationalCondition(
                        subject=subject,
                        operator=relational_operator,
                        target=element,
                    )
                )
                for element in condition._sorted_elements
            ]
            return MdxFunction.parentheses(
                [
                    reduce(
                        lambda accumulator, expression: MdxFunction.infix(
                            mdx_operator, [accumulator, expression]
                        ),
                        expressions,
                    )
                ]
            )


def _add_measure_filter(
    expression: MdxExpression,
    measure_conditions: Sequence[
        _CubeQueryFilterRelationalMeasureCondition
        | _CubeQueryFilterIsInMeasureCondition
    ],
    /,
) -> MdxExpression:
    if not measure_conditions:
        return expression

    logical_expression = (
        _generate_measure_filter_exression(measure_conditions[0])
        if len(measure_conditions) == 1
        else MdxFunction.infix(
            "AND",
            [
                _generate_measure_filter_exression(measure_condition)
                for measure_condition in measure_conditions
            ],
        )
    )
    return MdxFunction.function("Filter", [expression, logical_expression])


def _generate_mdx(
    *,
    conditions: Sequence[_CubeQueryFilterLeafCondition],
    cube: Cube,
    include_empty_rows: bool,
    include_totals: bool,
    level_identifiers: Sequence[LevelIdentifier],
    measure_identifiers: Sequence[MeasureIdentifier],
    scenario_name: str | None,
) -> MdxSelect:
    hierarchy_identifier_to_filter, deep_level_conditions, measure_conditions = (
        _process_conditions(
            conditions,
            cube=cube,
            scenario_name=scenario_name,
        )
    )

    deepest_levels = _keep_only_deepest_levels(level_identifiers, cube=cube)

    axes: list[MdxAxis[RegularAxisName]] = [
        _generate_columns_axis(
            measure_identifiers,
            # Only filter the COLUMNS axis if no levels were passed.
            measure_conditions=[] if deepest_levels else measure_conditions,
        )
    ]

    if deepest_levels:
        axes.append(
            _generate_rows_axis(
                deepest_levels,
                cube=cube,
                include_totals=include_totals,
                measure_conditions=measure_conditions,
                non_empty=not include_empty_rows,
            ),
        )

    hierarchy_filter_class_from_expressions: dict[
        tuple[MdxExpression, ...], _FilterClass
    ] = {
        **{
            (_generate_level_filter_expression(condition),): "sub_select"
            for condition in deep_level_conditions
        },
        **dict(
            _generate_hierarchy_filter_expressions_and_class(
                hierarchy_filter,
                cube=cube,
                hierarchy_identifier=hierarchy_identifier,
                hierarchy_on_regular_axis=any(
                    level_identifier.hierarchy_identifier == hierarchy_identifier
                    for level_identifier in deepest_levels
                ),
            )
            for hierarchy_identifier, hierarchy_filter in hierarchy_identifier_to_filter.items()
        ),
    }

    mdx_select = MdxSelect(axes=axes, from_clause=MdxFromClause(cube_name=cube.name))

    return _add_hierarchy_filters(mdx_select, hierarchy_filter_class_from_expressions)


def generate_mdx(
    *,
    cube: Cube,
    filter: CubeQueryFilterCondition | None = None,  # noqa: A002
    include_empty_rows: bool = False,
    include_totals: bool = False,
    level_identifiers: Sequence[LevelIdentifier] = (),
    measure_identifiers: Sequence[MeasureIdentifier] = (),
    scenario: str | None = None,
) -> MdxSelect:
    dnf: tuple[tuple[_CubeQueryFilterLeafCondition, ...]] | None = (
        None if filter is None else dnf_from_condition(filter)
    )
    return _generate_mdx(
        conditions=() if dnf is None else dnf[0],
        cube=cube,
        include_empty_rows=include_empty_rows,
        include_totals=include_totals,
        level_identifiers=level_identifiers,
        measure_identifiers=measure_identifiers,
        scenario_name=scenario,
    )
