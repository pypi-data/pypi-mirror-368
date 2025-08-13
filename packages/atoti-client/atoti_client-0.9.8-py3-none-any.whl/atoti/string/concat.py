from __future__ import annotations

from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import MeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def concat(*measures: MeasureConvertible, separator: str = "") -> MeasureDefinition:
    """Concatenate measures together into a string.

    Args:
        measures: The string measures to concatenate together.
        separator: The separator to place between each measure value.
    """
    underlying_measures = [
        convert_to_measure_definition(measure) for measure in measures
    ]
    return GenericMeasure("STRING_CONCAT", separator, underlying_measures)
