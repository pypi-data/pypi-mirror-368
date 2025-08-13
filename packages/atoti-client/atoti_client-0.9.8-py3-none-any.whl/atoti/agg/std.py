from __future__ import annotations

from typing import overload

from .._doc import doc
from .._docs_utils import (
    STD_AND_VAR_DOC as _STD_AND_VAR_DOC,
    STD_DOC_KWARGS as _STD_DOC_KWARGS,
)
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..array.var import _Mode
from ..math import sqrt
from ..scope._scope import Scope
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    SCOPE_DOC as _SCOPE_DOC,
    LevelOrVariableColumnConvertible,
)
from .var import var


@overload
def std(
    operand: LevelOrVariableColumnConvertible,
    /,
    *,
    mode: _Mode = ...,
) -> MeasureDefinition: ...


@overload
def std(
    operand: VariableMeasureConvertible,
    /,
    *,
    mode: _Mode = ...,
    scope: Scope,
) -> MeasureDefinition: ...


@doc(
    _STD_AND_VAR_DOC,
    _SCOPE_DOC,
    **_STD_DOC_KWARGS,
    **_QUANTILE_STD_AND_VAR_DOC_KWARGS,
)
def std(
    operand: LevelOrVariableColumnConvertible | VariableMeasureConvertible,
    /,
    *,
    mode: _Mode = "sample",
    scope: Scope | None = None,
) -> MeasureDefinition:
    return sqrt(  # type: ignore[return-value] # pyright: ignore[reportReturnType]
        # The type checkers cannot see that the `@overload` above ensure that this call is valid.
        var(operand, mode=mode, scope=scope),  # type: ignore[arg-type,misc] # pyright: ignore[reportArgumentType]
    )
