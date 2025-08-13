from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from textwrap import dedent
from typing import Any, Final

from typing_extensions import override

from ..._constant import data_type_of, is_scalar
from ..._data_type import DataType
from ..._identification import ColumnIdentifier
from ..._py4j_client import Py4jClient
from ..._udaf_operation import (
    ColumnOperation,
    ConstantOperation,
    JavaFunctionOperation,
    Operation,
    TernaryOperation,
)
from ..java_operation_element import (
    BasicJavaOperationElement,
    JavaOperationElement,
    TernaryJavaOperationElement,
)
from ..java_operation_visitor import JavaOperation, OperationVisitor
from ..utils import get_column_reader_code

CONTRIBUTE_TEMPLATE = dedent(
    """\
protected void contribute(IArrayReader fact, IWritableBuffer aggregationBuffer) {{
    if (!fact.isNull(0)) {{
        {body}
    }}
}}
""",
)

DECONTRIBUTE_TEMPLATE = dedent(
    """\
protected void decontribute(IArrayReader fact, IWritableBuffer aggregationBuffer) {{
    if (!fact.isNull(0)) {{
        {body}
    }}
}}
""",
)

MERGE_TEMPLATE = dedent(
    """\
protected void merge(IArrayReader inputAggregationBuffer, IWritableBuffer outputAggregationBuffer) {{
    {body}
}}
""",
)

NULLABLE_MERGE_TEMPLATE = dedent(
    """\
protected void merge(IArrayReader inputAggregationBuffer, IWritableBuffer outputAggregationBuffer) {{
    if (!inputAggregationBuffer.isNull(0)) {{
        {body}
    }}
}}
""",
)

TERMINATE_TEMPLATE = dedent(
    """\
protected Object terminate(IArrayReader aggregationBuffer) {{
    if (aggregationBuffer.isNull(0)) {{
        return null;
    }} else {{
        {body}
    }}
}}
""",
)

_DATA_TYPE_TO_CONSTANT_VALUE_TO_JAVA_CODE: Mapping[DataType, Callable[[Any], str]] = {
    "String": lambda value: f'"{value}"',
    "int": lambda value: f"{value}",
    "long": lambda value: f"{value}L",
    "double": lambda value: f"{value}",
    "float": lambda value: f"{value}F",
    "LocalDate": lambda value: f"LocalDate.of({value.year}, {value.month}, {value.day})",
    "LocalDateTime": lambda value: f'LocalDateTime.parse("{value.isoformat()}")',
    "ZonedDateTime": lambda value: f'ZonedDateTime.parse("{value.isoformat()}")',
    "LocalTime": lambda value: f"LocalTime.of({value.hour}, {value.minute}, {value.second})",
}


class AggregationOperationVisitor(OperationVisitor, ABC):
    """Base OperationVisitor for building Java code for an aggregation function."""

    def __init__(self, *, columns: Sequence[ColumnIdentifier], py4j_client: Py4jClient):
        self.columns: Final = columns
        self.additional_methods_source_codes: Final[set[str]] = set()
        self.additional_imports: Final[set[str]] = set()
        self.py4j_client: Final = py4j_client

    @override
    def build_java_operation(self, operation: Operation) -> JavaOperation:
        operation_element = operation.accept(self)
        return JavaOperation(
            additional_imports=self.additional_imports,
            additional_methods_source_codes=self.additional_methods_source_codes,
            contribute_source_code=self._get_contribute_source_code(operation_element),
            decontribute_source_code=self._get_decontribute_source_code(
                operation_element,
            ),
            merge_source_code=self._get_merge_source_code(operation_element),
            terminate_source_code=self._get_terminate_source_code(operation_element),
            buffer_types=self._get_buffer_types(operation_element),
            output_type=operation_element.output_type,
        )

    @staticmethod
    @abstractmethod
    def _get_contribute_source_code(operation_element: JavaOperationElement) -> str: ...

    @staticmethod
    @abstractmethod
    def _get_decontribute_source_code(
        operation_element: JavaOperationElement,
    ) -> str | None: ...

    @staticmethod
    @abstractmethod
    def _get_merge_source_code(operation_element: JavaOperationElement) -> str: ...

    @staticmethod
    @abstractmethod
    def _get_terminate_source_code(operation_element: JavaOperationElement) -> str: ...

    @staticmethod
    @abstractmethod
    def _get_buffer_types(
        operation_element: JavaOperationElement,
    ) -> list[DataType]: ...

    @override
    def visit_column_operation(
        self,
        operation: ColumnOperation,
    ) -> JavaOperationElement:
        return BasicJavaOperationElement(
            java_source_code=get_column_reader_code(
                self.columns.index(operation._column_identifier),
                column_data_type=operation._column_data_type,
            ),
            _output_type=operation._column_data_type,
        )

    @override
    def visit_constant_operation(
        self,
        operation: ConstantOperation,
    ) -> JavaOperationElement:
        if not is_scalar(operation._value):
            raise NotImplementedError(
                f"Expected a scalar but got `{operation._value}`."
            )
        data_type = data_type_of(operation._value)
        return BasicJavaOperationElement(
            java_source_code=_DATA_TYPE_TO_CONSTANT_VALUE_TO_JAVA_CODE[data_type](
                operation._value
            ),
            _output_type=data_type,
        )

    @override
    def visit_ternary_operation(
        self,
        operation: TernaryOperation,
    ) -> JavaOperationElement:
        condition = operation.condition.accept(self)
        true_value = operation.true_operation.accept(self)
        false_value = (
            operation.false_operation.accept(self)
            if operation.false_operation is not None
            else None
        )
        if not isinstance(condition, BasicJavaOperationElement):
            raise TypeError(
                "Only BasicJavaOperationElements can be used as conditions, got "
                + str(condition),
            )
        return TernaryJavaOperationElement(
            condition_java_operation=condition,
            true_statement_java_operation=true_value,
            false_statement_java_operation=false_value,
        )

    @override
    def visit_java_function_operation(
        self,
        operation: JavaFunctionOperation,
    ) -> JavaOperationElement:
        java_function = operation.java_function
        # If the operation is a ternary operation, we need to bubble up the condition so they are all applied before any calculations are performed
        # i.e. (a < 2 ? (b > 3 ? c * 2, 3) + 2 : 3) would give us:
        # if (a < 2):
        #   if (b > 3):
        #       c * 2 + 2
        #   else:
        #       3 + 2
        # else:
        #   3
        # This makes it much easier to type check the various stages of the calculation and avoid errors when compiling the java code
        for index, underlying in enumerate(operation.underlyings):
            if isinstance(underlying, TernaryOperation):
                # Replace the TernaryOperation with the true operation
                true_operations = list(operation.underlyings)
                true_operations[index] = underlying.true_operation
                false_operations = list(operation.underlyings)
                if underlying.false_operation is not None:
                    # replace the ternary operation with the false operation
                    false_operations[index] = underlying.false_operation
                return TernaryOperation(
                    condition=underlying.condition,
                    # Call the java function on the new true_operations
                    true_operation=java_function(true_operations),
                    # Call the java function on the new false operations
                    false_operation=java_function(false_operations)
                    if underlying.false_operation is not None
                    else None,
                ).accept(self)
        # Once there are no more TernaryOperations in the underlyings, we can proceed
        java_function.add_method_source_codes(self.additional_methods_source_codes)
        java_function.update_class_imports(self.additional_imports)
        operation_elements = [
            underlying.accept(self) for underlying in operation.underlyings
        ]
        java_source_code = java_function.get_java_source_code(
            *operation_elements,
            py4j_client=self.py4j_client,
        )
        return BasicJavaOperationElement(
            java_source_code=java_source_code,
            _output_type=java_function.get_output_type_function()(
                operation_elements,
                self.py4j_client,
            ),
        )
