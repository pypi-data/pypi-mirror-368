from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def positive_values(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return a measure where all the elements < 0 of the passed array measure are replaced by 0."""
    check_array_type(measure)
    return CalculatedMeasure(
        Operator("positive_vector", [convert_to_measure_definition(measure)]),
    )
