from __future__ import annotations

from typing import overload

from .._doc import doc
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..scope._scope import Scope
from ._utils import (
    BASIC_ARGS_DOC as _BASIC_ARGS_DOC,
    BASIC_DOC as _BASIC_DOC,
    LevelOrVariableColumnConvertible,
)
from .quantile import quantile


@overload
def median(operand: LevelOrVariableColumnConvertible, /) -> MeasureDefinition: ...


@overload
def median(
    operand: VariableMeasureConvertible,
    /,
    *,
    scope: Scope,
) -> MeasureDefinition: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="median",
    example="""
        >>> m["Median Price"] = tt.agg.median(table["Price"])
        >>> cube.query(m["Median Price"])
          Median Price
        0        25.90""".replace("\n", "", 1),
)
def median(
    operand: LevelOrVariableColumnConvertible | VariableMeasureConvertible,
    /,
    *,
    scope: Scope | None = None,
) -> MeasureDefinition:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return quantile(operand, q=0.5, scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
