from __future__ import annotations

from typing import overload

from .._doc import doc
from .._docs_utils import QUANTILE_DOC as _QUANTILE_DOC
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..array import quantile as array_quantile
from ..array.quantile import _Interpolation, _Mode, _Quantile
from ..scope._scope import Scope
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    SCOPE_DOC as _SCOPE_DOC,
    LevelOrVariableColumnConvertible,
)
from ._vector import vector


@overload
def quantile(
    operand: LevelOrVariableColumnConvertible,
    /,
    q: _Quantile,
    *,
    mode: _Mode = ...,
    interpolation: _Interpolation = ...,
) -> MeasureDefinition: ...


@overload
def quantile(
    operand: VariableMeasureConvertible,
    /,
    q: _Quantile,
    *,
    mode: _Mode = ...,
    interpolation: _Interpolation = ...,
    scope: Scope,
) -> MeasureDefinition: ...


@doc(_QUANTILE_DOC, _SCOPE_DOC, **_QUANTILE_STD_AND_VAR_DOC_KWARGS)
def quantile(
    operand: LevelOrVariableColumnConvertible | VariableMeasureConvertible,
    /,
    q: _Quantile,
    *,
    mode: _Mode = "inc",
    interpolation: _Interpolation = "linear",
    scope: Scope | None = None,
) -> MeasureDefinition:
    return array_quantile(  # type: ignore[no-any-return,operator]
        # The type checkers cannot see that the `@overload` above ensure that this call is valid.
        vector(operand, scope=scope),  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
        q=q,
        mode=mode,
        interpolation=interpolation,
    )
