from __future__ import annotations

from collections.abc import Mapping, Sequence, Set as AbstractSet
from typing import Any, overload

from typing_extensions import deprecated

from .._constant import Scalar
from .._identification import ColumnIdentifier, Identifiable, identify
from .._measure.copy_measure import CopyMeasure, FullCopyMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..hierarchy import Hierarchy


@overload
def copy(
    measure: VariableMeasureConvertible | str,
    /,
    *,
    source: Mapping[Hierarchy, list[Any]],
    target: Mapping[Hierarchy, list[list[Any]]],
    member_names: list[str] | None = None,
) -> MeasureDefinition: ...


@overload
@deprecated("Use tt.consolidate()")
def copy(
    measure: VariableMeasureConvertible,
    /,
    *,
    hierarchy: Hierarchy,
    member_paths: Mapping[
        tuple[Scalar, ...],
        AbstractSet[tuple[Scalar, ...]],
    ],
    consolidation_factors: Sequence[Identifiable[ColumnIdentifier]] = (),
) -> MeasureDefinition: ...


def copy(
    measure: VariableMeasureConvertible | str,
    /,
    *,
    hierarchy: Hierarchy | None = None,
    member_paths: Mapping[
        tuple[Scalar, ...],
        AbstractSet[tuple[Scalar, ...]],
    ]
    | None = None,
    consolidation_factors: Sequence[Identifiable[ColumnIdentifier]] = (),
    source: Mapping[Hierarchy, list[Any]] | None = None,
    target: Mapping[Hierarchy, list[list[Any]]] | None = None,
    member_names: list[str] | None = None,
) -> MeasureDefinition:
    if hierarchy is not None or member_paths is not None or consolidation_factors:
        assert hierarchy is not None
        assert member_paths is not None
        columns = []
        for level_name in hierarchy:
            level = hierarchy[level_name]
            selection_field = level._selection_field
            assert selection_field
            columns.append(selection_field.column_identifier)

        return FullCopyMeasure(
            _underlying_measure=convert_to_measure_definition(measure),
            _hierarchy=hierarchy._identifier,
            _hierarchy_columns=tuple(columns),
            _member_paths=member_paths,
            _consolidation_factors=tuple(
                identify(column) for column in consolidation_factors
            ),
        )

    assert not (source is None and member_names is None)

    if source is None:
        source = {}

    if target is None:
        target = {}

    return CopyMeasure(
        _underlying_measure=measure
        if isinstance(measure, str)
        else convert_to_measure_definition(measure),
        _source={
            hierarchy._identifier: location for hierarchy, location in source.items()
        },
        _target={
            hierarchy._identifier: location for hierarchy, location in target.items()
        },
        _member_names=member_names if member_names is not None else set(),
    )
