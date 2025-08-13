from __future__ import annotations

import math
from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import final

from typing_extensions import override

from ._identification import (
    HasIdentifier,
    HierarchyIdentifier,
    Identifier,
    LevelIdentifier,
    MeasureIdentifier,
)
from ._measure_convertible import MeasureConvertible, MeasureOperand
from ._operation import (
    Condition,
    HierarchyMembershipCondition,
    IndexingOperation,
    LogicalCondition,
    MembershipCondition,
    NAryArithmeticOperation,
    Operation,
    RelationalCondition,
    UnaryArithmeticOperation,
)
from ._py4j_client import Py4jClient


@dataclass(eq=False, frozen=True, kw_only=True)
class MeasureDefinition(Operation[MeasureIdentifier]):
    """The definition of a :class:`~atoti.Measure` that has not been added to the cube yet."""

    @final
    def _distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        py4j_client: Py4jClient,
        cube_name: str,
    ) -> MeasureIdentifier:
        """Return the identifier of the measure, creating it in the cube if it does not exist yet."""
        name: str | None = self.__dict__.get("_name")
        if not name:
            name = self._do_distil(
                identifier,
                py4j_client=py4j_client,
                cube_name=cube_name,
            ).measure_name
            self.__dict__["_name"] = name
        elif identifier:
            # This measure has already been distilled, this is a copy with a different name.
            py4j_client.copy_measure(
                MeasureIdentifier(name),
                identifier,
                cube_name=cube_name,
            )
        assert isinstance(name, str)
        return MeasureIdentifier(name)

    @abstractmethod
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        py4j_client: Py4jClient,
        cube_name: str,
    ) -> MeasureIdentifier:
        """Create the measure in the cube and return its identifier."""

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset([MeasureIdentifier])


def convert_operand_to_measure_definition(
    value: MeasureOperand | None,
    /,
) -> MeasureDefinition:
    # pylint: disable=nested-import
    from ._measure.hierarchy_measure import HierarchyMeasure
    from ._measure.level_measure import LevelMeasure
    from ._measure.published_measure import PublishedMeasure

    # pylint: enable=nested-import

    match value:
        case None:
            raise TypeError(
                f"Cannot convert `{value}` operand to `{MeasureDefinition.__name__}`.",
            )
        case HierarchyIdentifier():
            return HierarchyMeasure(value)
        case LevelIdentifier():
            return LevelMeasure(value)
        case MeasureIdentifier():
            return PublishedMeasure(value.measure_name)
        case _:
            return convert_to_measure_definition(value)


def convert_to_measure_definition(  # noqa: C901, PLR0911, PLR0912, PLR0915
    value: MeasureConvertible,
    /,
) -> MeasureDefinition:
    # pylint: disable=nested-import
    from ._measure.boolean_measure import BooleanMeasure
    from ._measure.calculated_measure import CalculatedMeasure, Operator
    from ._measure.constant_measure import ConstantMeasure
    from ._measure.hierarchy_measure import HierarchyMeasure
    from ._measure.level_measure import LevelMeasure
    from ._measure.published_measure import PublishedMeasure

    # pylint: enable=nested-import

    if isinstance(value, MeasureDefinition):
        return value

    if isinstance(value, Condition):
        match value:
            case LogicalCondition(operands=operands, operator=operator):
                match operator:
                    case "&":
                        _operator: str = "and"
                    case "|":
                        _operator = "or"

                return BooleanMeasure(
                    _operator,
                    tuple(
                        convert_to_measure_definition(operand) for operand in operands
                    ),
                )
            case RelationalCondition(subject=subject, operator=operator, target=target):
                subject = convert_operand_to_measure_definition(subject)

                if target is None:
                    assert operator == "==" or operator == "!="

                    match operator:
                        case "==":
                            _operator = "isNull"
                        case "!=":
                            _operator = "notNull"

                    return BooleanMeasure(_operator, (subject,))

                match operator:
                    case "==":
                        _operator = "eq"
                    case "!=":
                        _operator = "ne"
                    case ">=":
                        _operator = "ge"
                    case ">":
                        _operator = "gt"
                    case "<=":
                        _operator = "le"
                    case "<":
                        _operator = "lt"

                return BooleanMeasure(
                    _operator,
                    (subject, convert_operand_to_measure_definition(target)),
                )
            case HierarchyMembershipCondition() | MembershipCondition():
                return convert_to_measure_definition(value._logical_relational())

    if isinstance(value, HasIdentifier):
        identifier = value._identifier

        if isinstance(identifier, LevelIdentifier):
            return LevelMeasure(identifier)

        if isinstance(identifier, HierarchyIdentifier):
            return HierarchyMeasure(identifier)

        assert isinstance(identifier, MeasureIdentifier)
        return PublishedMeasure(identifier.measure_name)

    if isinstance(value, Operation):
        match value:
            case IndexingOperation():
                if isinstance(value.index, slice):
                    if value.index.step:
                        raise ValueError(
                            "Cannot index an array measure using a slice with a step.",
                        )
                    start = value.index.start if value.index.start is not None else 0
                    stop = (
                        value.index.stop if value.index.stop is not None else math.inf
                    )
                    return CalculatedMeasure(
                        Operator(
                            "vector_sub",
                            [
                                convert_operand_to_measure_definition(value.operand),
                                convert_to_measure_definition(start),
                                convert_to_measure_definition(stop),
                            ],
                        ),
                    )

                return CalculatedMeasure(
                    Operator(
                        "vector_element",
                        [
                            convert_operand_to_measure_definition(value.operand),
                            convert_operand_to_measure_definition(
                                tuple(value.index)
                                if isinstance(value.index, Sequence)
                                else value.index
                            ),
                        ],
                    ),
                )
            case NAryArithmeticOperation():
                match value.operator:
                    case "+":
                        _operator = "add"
                    case "//":
                        _operator = "floordiv"
                    case "%":
                        _operator = "mod"
                    case "*":
                        _operator = "mul"
                    case "**":
                        _operator = "pow"
                    case "-":
                        _operator = "sub"
                    case "/":
                        _operator = "truediv"

                return CalculatedMeasure(
                    Operator(
                        _operator,
                        [
                            convert_operand_to_measure_definition(operand)
                            for operand in value.operands
                        ],
                    ),
                )
            case UnaryArithmeticOperation():
                match value.operator:
                    case "-":
                        _operator = "neg"

                return CalculatedMeasure(
                    Operator(
                        _operator,
                        [convert_operand_to_measure_definition(value.operand)],
                    ),
                )
            case _:
                raise TypeError(f"Unexpected operation type: `{type(value)}`.")

    return ConstantMeasure(_value=value)
