from __future__ import annotations

from collections.abc import Sequence

from .._identification import ColumnIdentifier, Identifiable, identify
from .._measure.consolidated_measure import ConsolidateMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..hierarchy import Hierarchy


def consolidate(
    measure: VariableMeasureConvertible | str,
    /,
    *,
    hierarchy: Hierarchy,
    factors: Sequence[Identifiable[ColumnIdentifier]],
) -> MeasureDefinition:
    columns = []
    for level_name in hierarchy:
        level = hierarchy[level_name]
        selection_field = level._selection_field
        assert selection_field
        columns.append(selection_field.column_identifier)
    return ConsolidateMeasure(
        _underlying_measure=convert_to_measure_definition(measure),
        _hierarchy=hierarchy._identifier,
        _level_columns=tuple(columns),
        _factors=tuple(identify(column) for column in factors),
    )
