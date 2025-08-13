from __future__ import annotations

from textwrap import dedent
from typing import final

from typing_extensions import override

from ..._data_type import DataType, is_numeric_array_type, is_numeric_type
from ...type import INT
from ..java_operation_element import JavaOperationElement
from ..utils import get_buffer_add_code, get_buffer_read_code, get_terminate_code
from ._aggregation_operation_visitor import (
    CONTRIBUTE_TEMPLATE,
    DECONTRIBUTE_TEMPLATE,
    MERGE_TEMPLATE,
    TERMINATE_TEMPLATE,
    AggregationOperationVisitor,
)


def _get_contribute_numeric_code(
    operation_element: JavaOperationElement,
) -> str:
    return dedent(
        """\
        {buffer_add_code}
        aggregationBuffer.addInt(1, 1);
    """,
    ).format(
        buffer_add_code=get_buffer_add_code(
            buffer_code="aggregationBuffer",
            value_code="{java_source_code}",
            output_type=operation_element.output_type,
        ),
    )


def _get_decontribute_numeric_code(
    operation_element: JavaOperationElement,
) -> str:
    return dedent(
        """\
        {buffer_add_code}
        aggregationBuffer.addInt(1, -1);
    """,
    ).format(
        buffer_add_code=get_buffer_add_code(
            buffer_code="aggregationBuffer",
            value_code="-1 * {java_source_code}",
            output_type=operation_element.output_type,
        ),
    )


@final
class MeanAggregationOperationVisitor(AggregationOperationVisitor):
    """Implementation of the AggregationOperationVisitor to build the source code for a ``MEAN`` aggregation function."""

    @staticmethod
    @override
    def _get_contribute_source_code(operation_element: JavaOperationElement) -> str:
        numeric_code = (
            _get_contribute_numeric_code(operation_element)
            if is_numeric_type(operation_element.output_type)
            else None
        )
        array_code = dedent(
            """\
            if (aggregationBuffer.isNull(0)) {{
                aggregationBuffer.write(0, {java_source_code});
                aggregationBuffer.addInt(1, 1);
            }} else {{
                IVector value = {java_source_code};
                if (value != null) {{
                    aggregationBuffer.readWritableVector(0).plus(value);
                    aggregationBuffer.addInt(1, 1);
                }}
            }}
        """,
        )
        body = operation_element.get_java_source_code(
            numeric_code=numeric_code,
            array_code=array_code,
        )
        return CONTRIBUTE_TEMPLATE.format(body=body)

    @staticmethod
    @override
    def _get_decontribute_source_code(
        operation_element: JavaOperationElement,
    ) -> str | None:
        numeric_code = (
            _get_decontribute_numeric_code(operation_element)
            if is_numeric_type(operation_element.output_type)
            else None
        )
        array_code = dedent(
            """\
            if (!aggregationBuffer.isNull(0)) {{
                aggregationBuffer.readWritableVector(0).minus({java_source_code});
                aggregationBuffer.addInt(1, -1);
            }}
        """,
        )
        body = operation_element.get_java_source_code(
            numeric_code=numeric_code,
            array_code=array_code,
        )
        return DECONTRIBUTE_TEMPLATE.format(body=body)

    @staticmethod
    @override
    def _get_merge_source_code(operation_element: JavaOperationElement) -> str:
        if is_numeric_type(operation_element.output_type):
            buffer_add_code = get_buffer_add_code(
                buffer_code="outputAggregationBuffer",
                value_code=get_buffer_read_code(
                    buffer_code="inputAggregationBuffer",
                    output_type=operation_element.output_type,
                ),
                output_type=operation_element.output_type,
            )

            body = dedent(
                """\
                {buffer_add_code}
                outputAggregationBuffer.addInt(1, inputAggregationBuffer.readInt(1));
            """,
            ).format(buffer_add_code=buffer_add_code)
            return MERGE_TEMPLATE.format(body=body)
        if is_numeric_array_type(operation_element.output_type):
            body = dedent(
                """\
                if (!inputAggregationBuffer.isNull(0)) {
                    if (outputAggregationBuffer.isNull(0)) {
                        outputAggregationBuffer.write(0, inputAggregationBuffer.readVector(0));
                    } else {
                        outputAggregationBuffer.readWritableVector(0).plus(inputAggregationBuffer.readVector(0));
                    }
                    outputAggregationBuffer.addInt(1, inputAggregationBuffer.readInt(1));
                }
            """,
            )
            return MERGE_TEMPLATE.format(body=body)

        raise TypeError("Unsupported output type " + str(operation_element.output_type))

    @staticmethod
    @override
    def _get_terminate_source_code(operation_element: JavaOperationElement) -> str:
        if is_numeric_type(operation_element.output_type):
            buffer_sum = get_buffer_read_code(
                buffer_code="aggregationBuffer",
                output_type=operation_element.output_type,
            )
            mean = f"{buffer_sum} / aggregationBuffer.readInt(1)"
            return_value = get_terminate_code(operation_element.output_type, mean)
            body = f"return {return_value};"
            return TERMINATE_TEMPLATE.format(body=body)
        if is_numeric_array_type(operation_element.output_type):
            body = dedent(
                """\
                IVector out = aggregationBuffer.readVector(0);
                out.scale(1 / aggregationBuffer.readDouble(1)); // 0 if we use readInt
                return out;\n
            """,
            )
            return TERMINATE_TEMPLATE.format(body=body)
        raise TypeError("Unsupported output type " + str(operation_element.output_type))

    @staticmethod
    @override
    def _get_buffer_types(
        operation_element: JavaOperationElement,
    ) -> list[DataType]:
        return [operation_element.output_type, INT]
