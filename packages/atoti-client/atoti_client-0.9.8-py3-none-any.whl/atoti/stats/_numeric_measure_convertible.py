from typing import TypeAlias

from .._measure_convertible import VariableMeasureConvertible

NumericMeasureConvertible: TypeAlias = int | float | VariableMeasureConvertible
