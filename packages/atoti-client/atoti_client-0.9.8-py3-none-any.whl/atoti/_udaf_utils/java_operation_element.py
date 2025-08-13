from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final

from typing_extensions import override

from .._data_type import DataType, is_numeric_array_type, is_numeric_type


class JavaOperationElement(ABC):
    """Operation's which have been processed and can be converted into compilable Java code."""

    @abstractmethod
    def get_java_source_code(
        self,
        *,
        numeric_code: str | None = None,
        array_code: str | None = None,
    ) -> str:
        """Retrieve the Java code for the current operation element."""

    @property
    @abstractmethod
    def output_type(self) -> DataType:
        """Get the output type of the current operation element."""


@final
@dataclass(frozen=True, kw_only=True)
class BasicJavaOperationElement(JavaOperationElement):
    """JavaOperationElement for operations without conditions."""

    java_source_code: str
    _output_type: DataType

    @property
    @override
    def output_type(self) -> DataType:
        return self._output_type

    @override
    def get_java_source_code(
        self,
        *,
        numeric_code: str | None = None,
        array_code: str | None = None,
    ) -> str:
        if numeric_code is None and array_code is None:
            return self.java_source_code

        if is_numeric_type(self._output_type) and numeric_code is not None:
            return numeric_code.format(java_source_code=self.java_source_code)
        if is_numeric_array_type(self._output_type) and array_code is not None:
            return array_code.format(java_source_code=self.java_source_code)
        return self.java_source_code


@final
@dataclass(frozen=True, kw_only=True)
class TernaryJavaOperationElement(JavaOperationElement):
    """JavaOperationElement for operations which contain conditions."""

    true_false_template = """
        if ({condition_code}) {{
            {true_statement_code}
        }} else {{
            {false_statement_code}
        }}
    """

    true_template = """
        if ({condition_code}) {{
            {true_statement_code}
        }}
    """

    condition_java_operation: BasicJavaOperationElement
    true_statement_java_operation: JavaOperationElement
    false_statement_java_operation: JavaOperationElement | None

    @override
    def get_java_source_code(
        self,
        *,
        numeric_code: str | None = None,
        array_code: str | None = None,
    ) -> str:
        if self.false_statement_java_operation is not None:
            return self.true_false_template.format(
                condition_code=self.condition_java_operation.get_java_source_code(),
                true_statement_code=self.true_statement_java_operation.get_java_source_code(
                    numeric_code=numeric_code,
                    array_code=array_code,
                ),
                false_statement_code=self.false_statement_java_operation.get_java_source_code(
                    numeric_code=numeric_code,
                    array_code=array_code,
                ),
            )

        return self.true_template.format(
            condition_code=self.condition_java_operation.get_java_source_code(),
            true_statement_code=self.true_statement_java_operation.get_java_source_code(
                numeric_code=numeric_code,
                array_code=array_code,
            ),
        )

    @property
    @override
    def output_type(self) -> DataType:
        if self.false_statement_java_operation is None:
            return self.true_statement_java_operation.output_type

        if (
            is_numeric_type(self.true_statement_java_operation.output_type)
            and is_numeric_type(self.false_statement_java_operation.output_type)
        ) or (
            self.true_statement_java_operation.output_type
            == self.false_statement_java_operation.output_type
        ):
            return self.true_statement_java_operation.output_type

        raise ValueError("Both paths of the condition must return the same value type.")
