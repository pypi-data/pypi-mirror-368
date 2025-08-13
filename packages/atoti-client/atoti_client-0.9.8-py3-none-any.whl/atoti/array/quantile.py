from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import Field

from .._doc import doc
from .._docs_utils import QUANTILE_DOC as _QUANTILE_DOC
from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    check_array_type,
)

_Interpolation = Literal["linear", "higher", "lower", "nearest", "midpoint"]
_Mode = Literal["simple", "centered", "inc", "exc"]


_Q = Annotated[float, Field(ge=0, le=1)]
_Quantile: TypeAlias = _Q | VariableMeasureConvertible


@doc(_QUANTILE_DOC, **_QUANTILE_STD_AND_VAR_DOC_KWARGS)
def quantile(
    measure: VariableMeasureConvertible,
    /,
    q: _Quantile,
    *,
    mode: _Mode = "inc",
    interpolation: _Interpolation = "linear",
) -> MeasureDefinition:
    check_array_type(measure)
    return GenericMeasure(
        "CALCULATED_QUANTILE",
        mode,
        interpolation,
        [convert_to_measure_definition(arg) for arg in [measure, q]],
    )
