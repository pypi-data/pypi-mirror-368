from itertools import chain, product
from typing import Literal, overload

from .operation import (
    ConditionBound,
    LogicalCondition,
    LogicalConditionLeafOperandBound,
    LogicalConditionLeafOperandT_co,
)
from .operator import LogicalOperator


@overload
def dnf_from_condition(
    condition: LogicalConditionLeafOperandT_co,  # type: ignore[misc]
    /,
) -> tuple[tuple[LogicalConditionLeafOperandT_co]]: ...


@overload
def dnf_from_condition(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
    condition: LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, Literal["&"]],
    /,
) -> tuple[tuple[LogicalConditionLeafOperandT_co, ...]]: ...


@overload
def dnf_from_condition(
    condition: LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, Literal["|"]],
    /,
) -> tuple[tuple[LogicalConditionLeafOperandT_co], ...]: ...


@overload
def dnf_from_condition(
    condition: LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, LogicalOperator],
    /,
) -> tuple[tuple[LogicalConditionLeafOperandT_co], ...]: ...


def dnf_from_condition(
    condition: ConditionBound,
    /,
) -> tuple[tuple[LogicalConditionLeafOperandBound, ...], ...]:
    """Decombine the passed condition into leave conditions in disjunctive normal form.

    For example: ``foo & (bar | baz)`` will return ``((foo, bar), (foo, baz))``.
    """
    if not isinstance(condition, LogicalCondition):
        return ((condition,),)

    disjunctive_normal_forms = [
        dnf_from_condition(operand) for operand in condition.operands
    ]

    match condition.operator:
        case "&":
            return tuple(
                tuple(chain.from_iterable(conditions))
                for conditions in product(*disjunctive_normal_forms)
            )
        case "|":
            return tuple(chain.from_iterable(disjunctive_normal_forms))
