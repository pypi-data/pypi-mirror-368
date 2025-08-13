from __future__ import annotations

from typing import Literal

from .._doc import doc
from .._docs_utils import (
    STD_AND_VAR_DOC as _STD_AND_VAR_DOC,
    VAR_DOC_KWARGS as _VAR_DOC_KWARGS,
)
from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    check_array_type,
)

_Mode = Literal["sample", "population"]


@doc(_STD_AND_VAR_DOC, **_VAR_DOC_KWARGS, **_QUANTILE_STD_AND_VAR_DOC_KWARGS)
def var(
    measure: VariableMeasureConvertible,
    /,
    *,
    mode: _Mode = "sample",
) -> MeasureDefinition:
    check_array_type(measure)
    return CalculatedMeasure(
        Operator("variance", [convert_to_measure_definition(measure), mode]),
    )
