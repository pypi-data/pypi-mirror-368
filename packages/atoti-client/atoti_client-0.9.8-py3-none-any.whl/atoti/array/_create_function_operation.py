from __future__ import annotations

from .._column_convertible import ColumnConvertible, ColumnOperation
from .._function_operation import FunctionOperation
from .._operation import convert_to_operand


def create_function_operation(
    *operands: ColumnConvertible | None,
    function_key: str,
) -> ColumnOperation:
    return FunctionOperation(
        function_key=function_key,
        operands=tuple(convert_to_operand(operand) for operand in operands),
    )
