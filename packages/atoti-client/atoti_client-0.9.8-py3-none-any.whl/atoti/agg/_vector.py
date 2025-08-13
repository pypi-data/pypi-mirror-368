from __future__ import annotations

from typing import overload

from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition
from ..scope._scope import Scope
from ._agg import agg
from ._utils import LevelOrVariableColumnConvertible


@overload
def vector(operand: LevelOrVariableColumnConvertible, /) -> MeasureDefinition: ...


@overload
def vector(
    operand: VariableMeasureConvertible,
    /,
    *,
    scope: Scope,
) -> MeasureDefinition: ...


def vector(
    operand: LevelOrVariableColumnConvertible | VariableMeasureConvertible,
    /,
    *,
    scope: Scope | None = None,
) -> MeasureDefinition:
    """Return an array measure representing the values of the passed operand across the specified scope."""
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="VECTOR", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
