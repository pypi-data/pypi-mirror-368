from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import cache, cached_property
from threading import Lock
from typing import Final, final

from typing_extensions import override

from .._column_convertible import ColumnCondition, ColumnOperation as _ColumnOperation
from .._data_type import DataType
from .._function_operation import FunctionOperation
from .._identification import ColumnIdentifier, MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._operation import (
    Condition,
    NAryArithmeticOperation,
    Operand,
    Operation as _Operation,
    RelationalCondition,
    UnaryArithmeticOperation,
    dnf_from_condition,
)
from .._py4j_client import Py4jClient
from .._udaf_operation import (
    AdditionOperation,
    ColumnOperation,
    ConstantOperation,
    DivisionOperation,
    EqualOperation,
    GreaterThanOperation,
    GreaterThanOrEqualOperation,
    JavaFunctionOperation,
    LowerThanOperation,
    LowerThanOrEqualOperation,
    MultiplicationOperation,
    NotEqualOperation,
    Operation,
    SubtractionOperation,
    TernaryOperation,
)
from .._udaf_utils import (
    ARRAY_MEAN,
    ARRAY_SUM,
    LongAggregationOperationVisitor,
    MaxAggregationOperationVisitor,
    MeanAggregationOperationVisitor,
    MinAggregationOperationVisitor,
    MultiplyAggregationOperationVisitor,
    OperationVisitor,
    ShortAggregationOperationVisitor,
    SingleValueNullableAggregationOperationVisitor,
    SquareSumAggregationOperationVisitor,
    SumAggregationOperationVisitor,
)
from .._where_operation import WhereOperation

OPERATION_VISITORS = {
    "SUM": SumAggregationOperationVisitor,
    "MEAN": MeanAggregationOperationVisitor,
    "MULTIPLY": MultiplyAggregationOperationVisitor,
    "MIN": MinAggregationOperationVisitor,
    "MAX": MaxAggregationOperationVisitor,
    "SQ_SUM": SquareSumAggregationOperationVisitor,
    "SHORT": ShortAggregationOperationVisitor,
    "LONG": LongAggregationOperationVisitor,
    "SINGLE_VALUE_NULLABLE": SingleValueNullableAggregationOperationVisitor,
}


@final
class _AtomicCounter:
    """Threadsafe counter to get unique IDs."""

    def __init__(self) -> None:
        self._value = 0
        self._lock: Final = Lock()

    def read_and_increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value


@cache
def _get_id_provider() -> _AtomicCounter:
    return _AtomicCounter()


@final
@dataclass(frozen=True, kw_only=True)
class _UserDefinedAggregateFunction:
    """A class template which builds the sources to compile an AUserDefinedAggregate function at runtime.

    This class parses the combination of operations passed and converts them into Java source code blocks.
    These source code blocks are then compiled using Javassist into a new aggregation function which is then registered on the session.
    """

    _operation: Operation
    _plugin_key: str

    @property
    def _columns(self) -> Sequence[ColumnIdentifier]:
        return self._operation.columns

    @cached_property
    def plugin_key(self) -> str:
        column_names = "".join([column.column_name for column in self._columns])
        return f"{column_names}{_get_id_provider().read_and_increment()}.{self._plugin_key}"

    def register_aggregation_function(self, *, py4j_client: Py4jClient) -> None:
        """Generate the required Java source code blocks and pass them to the Java process to be compiled into a new UserDefinedAggregateFunction."""
        visitor_class = OPERATION_VISITORS[self._plugin_key]
        visitor: OperationVisitor = visitor_class(  # type: ignore[abstract]
            columns=self._columns,
            py4j_client=py4j_client,
        )

        java_operation = visitor.build_java_operation(self._operation)
        py4j_client.register_aggregation_function(
            additional_imports=java_operation.additional_imports,
            additional_methods=java_operation.additional_methods_source_codes,
            contribute_source_code=java_operation.contribute_source_code,
            decontribute_source_code=java_operation.decontribute_source_code,
            merge_source_code=java_operation.merge_source_code,
            terminate_source_code=java_operation.terminate_source_code,
            buffer_types=java_operation.buffer_types,
            output_type=java_operation.output_type,
            plugin_key=self.plugin_key,
        )


def _operand_to_udaf_operation(  # noqa: C901, PLR0911, PLR0912
    operand: Operand[ColumnIdentifier] | Operation,
    /,
    *,
    get_column_data_type: Callable[[ColumnIdentifier], DataType],
) -> Operation:
    if isinstance(operand, Condition):
        dnf = dnf_from_condition(operand)
        assert len(dnf) == 1
        assert len(dnf[0]) == 1
        condition = dnf[0][0]
        assert isinstance(condition, RelationalCondition)
        assert condition.target is not None
        left_operand, right_operand = (
            _operand_to_udaf_operation(
                # Mypy is flaky here, try removing `unused-ignore` when upgrading it.
                sub_operand,  # type: ignore[arg-type,unused-ignore]
                get_column_data_type=get_column_data_type,
            )
            for sub_operand in (condition.subject, condition.target)
        )
        match condition.operator:
            case "==":
                return EqualOperation(left_operand, right_operand)
            case ">=":
                return GreaterThanOrEqualOperation(left_operand, right_operand)
            case ">":
                return GreaterThanOperation(left_operand, right_operand)
            case "<=":
                return LowerThanOrEqualOperation(left_operand, right_operand)
            case "<":
                return LowerThanOperation(left_operand, right_operand)
            case "!=":
                return NotEqualOperation(left_operand, right_operand)

    match operand:
        case Operation():
            return operand
        case ColumnIdentifier():
            return ColumnOperation(operand, get_column_data_type(operand))
        case _Operation():
            match operand:
                case FunctionOperation(function_key=function_key, operands=operands):
                    match function_key:
                        case "array_mean":
                            return ARRAY_MEAN(operands[0])
                        case "array_sum":
                            return ARRAY_SUM(operands[0])
                        case _:
                            raise NotImplementedError(
                                f"Unsupported function key: `{function_key}`."
                            )
                case NAryArithmeticOperation(operands=operands, operator=operator):
                    left_operand, right_operand = (
                        _operand_to_udaf_operation(
                            sub_operand,  # type: ignore[arg-type]
                            get_column_data_type=get_column_data_type,
                        )
                        for sub_operand in operands
                    )
                    match operator:
                        case "+":
                            return AdditionOperation(left_operand, right_operand)
                        case "*":
                            return MultiplicationOperation(left_operand, right_operand)
                        case "-":
                            return SubtractionOperation(left_operand, right_operand)
                        case "/":
                            return DivisionOperation(left_operand, right_operand)
                        case "//" | "%" | "**":
                            raise NotImplementedError(
                                f"Unsupported arithmetic operator: `{operator}`."
                            )
                case UnaryArithmeticOperation(operand=_operand, operator=operator):
                    match operator:
                        case "-":
                            raise NotImplementedError(
                                f"Unsupported arithmetic operator: `{operator}`."
                            )
                case WhereOperation(
                    condition=where_condition,
                    true_value=true_value,
                    false_value=false_value,
                ):
                    return TernaryOperation(
                        condition=_operand_to_udaf_operation(
                            where_condition,
                            get_column_data_type=get_column_data_type,
                        ),
                        true_operation=_operand_to_udaf_operation(
                            true_value,
                            get_column_data_type=get_column_data_type,
                        ),
                        false_operation=None
                        if false_value is None
                        else _operand_to_udaf_operation(
                            false_value,
                            get_column_data_type=get_column_data_type,
                        ),
                    )
                case _:
                    raise TypeError(f"Unsupported operation: `{operand}`.")
        case _:
            return ConstantOperation(operand)


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class UdafMeasure(MeasureDefinition):
    _plugin_key: str
    _operation: ColumnCondition | _ColumnOperation | JavaFunctionOperation

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        cube_name: str,
        py4j_client: Py4jClient,
    ) -> MeasureIdentifier:
        udaf_operation = _operand_to_udaf_operation(
            self._operation,
            get_column_data_type=lambda identifier: py4j_client.get_column_data_type(
                identifier,
            ),
        )
        udaf = _UserDefinedAggregateFunction(
            _operation=udaf_operation,
            _plugin_key=self._plugin_key,
        )
        udaf.register_aggregation_function(py4j_client=py4j_client)
        return py4j_client.create_measure(
            identifier,
            "ATOTI_UDAF_MEASURE",
            udaf._columns,
            udaf.plugin_key,
            self._plugin_key,
            cube_name=cube_name,
        )
