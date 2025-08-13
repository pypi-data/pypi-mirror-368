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
def sum(  # noqa: A001
    operand: LevelOrVariableColumnConvertible,
    /,
) -> MeasureDefinition: ...


@overload
def sum(  # noqa: A001
    operand: VariableMeasureConvertible,
    /,
    *,
    scope: Scope,
) -> MeasureDefinition: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="sum",
    example="""
        >>> m["Quantity.SUM"] = tt.agg.sum(table["Quantity"])
        >>> cube.query(m["Quantity.SUM"])
          Quantity.SUM
        0        1,110""".replace("\n", "", 1),
)
def sum(  # noqa: A001
    operand: LevelOrVariableColumnConvertible | VariableMeasureConvertible,
    /,
    *,
    scope: Scope | None = None,
) -> MeasureDefinition:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="SUM", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
