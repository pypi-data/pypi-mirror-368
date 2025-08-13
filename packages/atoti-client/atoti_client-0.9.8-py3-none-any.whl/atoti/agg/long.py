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
def long(operand: LevelOrVariableColumnConvertible, /) -> MeasureDefinition: ...


@overload
def long(
    operand: VariableMeasureConvertible,
    /,
    *,
    scope: Scope,
) -> MeasureDefinition: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="sum of the positive values",
    example="""
        >>> m["Quantity.LONG"] = tt.agg.long(table["Quantity"])
        >>> cube.query(m["Quantity.LONG"])
          Quantity.LONG
        0         1,110""".replace("\n", "", 1),
)
def long(
    operand: LevelOrVariableColumnConvertible | VariableMeasureConvertible,
    /,
    *,
    scope: Scope | None = None,
) -> MeasureDefinition:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="LONG", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
