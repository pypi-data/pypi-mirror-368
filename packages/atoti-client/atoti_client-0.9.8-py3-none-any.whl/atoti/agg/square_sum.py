from __future__ import annotations

from typing import overload

from .._doc import doc
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..scope._scope import Scope
from ._agg import agg
from ._utils import (
    BASIC_ARGS_DOC as _BASIC_ARGS_DOC,
    BASIC_DOC as _BASIC_DOC,
    LevelOrVariableColumnConvertible,
)


@overload
def square_sum(
    operand: LevelOrVariableColumnConvertible,
    /,
) -> MeasureDefinition: ...


@overload
def square_sum(
    operand: VariableMeasureConvertible,
    /,
    *,
    scope: Scope,
) -> MeasureDefinition: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="sum of the square",
    example="""
        >>> m["Other.SQUARE_SUM"] = tt.agg.square_sum(table["Other"])
        >>> cube.query(m["Other.SQUARE_SUM"])
          Other.SQUARE_SUM
        0                9""".replace("\n", "", 1),
)
def square_sum(
    operand: LevelOrVariableColumnConvertible | VariableMeasureConvertible,
    /,
    *,
    scope: Scope | None = None,
) -> MeasureDefinition:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="SQ_SUM", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
