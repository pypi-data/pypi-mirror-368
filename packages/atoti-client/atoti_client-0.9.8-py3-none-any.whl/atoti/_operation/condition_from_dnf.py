from collections.abc import Sequence
from typing import Literal, overload

from .operation import (
    LogicalCondition,
    LogicalConditionLeafOperandT_co,
    LogicalConditionOperatorT_co,
    OtherLogicalConditionOperatorT,
)
from .operator import LogicalOperator


def _combine(
    *conditions: LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, LogicalConditionOperatorT_co],
    operator: OtherLogicalConditionOperatorT,
) -> (
    LogicalConditionLeafOperandT_co
    | LogicalCondition[
        LogicalConditionLeafOperandT_co,
        LogicalOperator | OtherLogicalConditionOperatorT,
    ]
):
    match conditions:
        case ():
            raise ValueError("No conditions to combine.")
        case (condition,):
            return condition
        case _:
            return LogicalCondition(operands=conditions, operator=operator)


@overload
def condition_from_dnf(
    leave_conditions: tuple[tuple[LogicalConditionLeafOperandT_co]],
    /,
) -> LogicalConditionLeafOperandT_co: ...


@overload
def condition_from_dnf(  # type: ignore[overload-overlap]
    leave_conditions: tuple[Sequence[LogicalConditionLeafOperandT_co]],
    /,
) -> (
    LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, Literal["&"]]
): ...


@overload
def condition_from_dnf(
    leave_conditions: Sequence[tuple[LogicalConditionLeafOperandT_co]],
    /,
) -> (
    LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, Literal["|"]]
): ...


@overload
def condition_from_dnf(
    leave_conditions: Sequence[Sequence[LogicalConditionLeafOperandT_co]],
    /,
) -> (
    LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, LogicalOperator]
): ...


def condition_from_dnf(
    leave_conditions: Sequence[Sequence[LogicalConditionLeafOperandT_co]],
    /,
) -> (
    LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, LogicalOperator]
):
    """Return a single condition from leave conditions in disjunctive normal form.

    For example: ``((foo, bar), (foo, baz))`` will return ``foo & (bar | baz)``.
    """
    return _combine(
        *(
            _combine(*conjunct_conditions, operator="&")
            for conjunct_conditions in leave_conditions
        ),
        operator="|",
    )
