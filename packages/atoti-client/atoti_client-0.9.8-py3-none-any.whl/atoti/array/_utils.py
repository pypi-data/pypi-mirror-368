from __future__ import annotations

from .._data_type import is_array_type
from .._data_type_error import DataTypeError
from .._measure_convertible import MeasureConvertible
from ..measure import Measure

QUANTILE_STD_AND_VAR_DOC_KWARGS = {
    "measure_or_operand": "measure",
    "what": "of the elements of the passed array measure",
}


def check_array_type(measure: MeasureConvertible) -> None:
    if isinstance(measure, Measure) and not is_array_type(measure.data_type):
        message = (
            "Incorrect measure type."
            f" Expected measure {measure.name} to be of type array but got {measure.data_type}."
        )
        raise DataTypeError(message)
