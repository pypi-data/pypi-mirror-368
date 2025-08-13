from abc import ABC, abstractmethod
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import final

from .._data_type import DataType
from .._udaf_operation import (
    ColumnOperation,
    ConstantOperation,
    JavaFunctionOperation,
    Operation,
    TernaryOperation,
)
from .java_operation_element import JavaOperationElement


@final
@dataclass(frozen=True, kw_only=True)
class JavaOperation:
    additional_imports: Collection[str]
    additional_methods_source_codes: Collection[str]
    contribute_source_code: str
    buffer_types: Sequence[DataType]
    decontribute_source_code: str | None
    merge_source_code: str
    output_type: DataType
    terminate_source_code: str


class OperationVisitor(ABC):
    """Visitor class to create java operations."""

    @abstractmethod
    def build_java_operation(self, operation: Operation) -> JavaOperation: ...

    @abstractmethod
    def visit_column_operation(
        self,
        operation: ColumnOperation,
    ) -> JavaOperationElement:
        """Convert a ``ColumnOperation`` into a ``JavaOperationElement``."""

    @abstractmethod
    def visit_constant_operation(
        self,
        operation: ConstantOperation,
    ) -> JavaOperationElement:
        """Convert a ``ConstOperation`` into a ``JavaOperationElement``."""

    @abstractmethod
    def visit_ternary_operation(
        self,
        operation: TernaryOperation,
    ) -> JavaOperationElement:
        """Convert a ``TernaryOperation`` into a ``JavaOperationElement``."""

    @abstractmethod
    def visit_java_function_operation(
        self,
        operation: JavaFunctionOperation,
    ) -> JavaOperationElement:
        """Convert a ``JavaFunctionOperation`` into a ``JavaOperationElement``."""
