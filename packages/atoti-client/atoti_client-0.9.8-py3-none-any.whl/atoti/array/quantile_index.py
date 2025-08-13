from __future__ import annotations

from typing import Literal

from .._doc import doc
from .._docs_utils import QUANTILE_INDEX_DOC as _QUANTILE_INDEX_DOC
from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    check_array_type,
)
from .quantile import _Mode, _Quantile


@doc(_QUANTILE_INDEX_DOC, **_QUANTILE_STD_AND_VAR_DOC_KWARGS)
def quantile_index(
    measure: VariableMeasureConvertible,
    /,
    q: _Quantile,
    *,
    mode: _Mode = "inc",
    interpolation: Literal["higher", "lower", "nearest"] = "lower",
) -> MeasureDefinition:
    check_array_type(measure)
    return GenericMeasure(
        "CALCULATED_QUANTILE_INDEX",
        mode,
        interpolation,
        [convert_to_measure_definition(arg) for arg in [measure, q]],
    )
