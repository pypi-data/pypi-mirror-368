from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def prefix_sum(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return a measure equal to the sum of the previous elements in the passed array measure.

    Example:
        If an array has the following values: ``[2.0, 1.0, 0.0, 3.0]``, the returned array will be: ``[2.0, 3.0, 3.0, 6.0]``.
    """
    check_array_type(measure)
    return CalculatedMeasure(
        Operator("prefix_sum", [convert_to_measure_definition(measure)]),
    )
