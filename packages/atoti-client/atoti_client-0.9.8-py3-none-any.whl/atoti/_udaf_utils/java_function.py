from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass
from textwrap import dedent
from time import time
from typing import Final, Literal, cast, final

from py4j.java_collections import ListConverter
from typing_extensions import override

from .._data_type import (
    DataType,
    NumericArrayDataType,
    NumericDataType,
    is_numeric_array_type,
    parse_data_type,
)
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .._py4j_client._utils import to_python_list
from .._typing import get_literal_args
from .._udaf_operation import (
    ColumnOperation,
    ConstantOperation,
    JavaFunctionOperation,
    Operation,
)
from ..type import LOCAL_DATE, LOCAL_DATE_TIME, LOCAL_TIME, STRING, ZONED_DATE_TIME
from .i_vector import I_VECTOR, IVectorType
from .java_operation_element import JavaOperationElement

_METHOD_TEMPLATE = dedent(
    """\
    public {output_type} {method_name}({input_string}) {{
        {method_body}
    }}
""",
)

_NUMERIC_ARRAY_DATA_TYPES = cast(
    tuple[NumericArrayDataType, ...],
    get_literal_args(NumericArrayDataType),
)
_NUMERIC_DATA_TYPES = cast(
    tuple[NumericDataType, ...],
    get_literal_args(NumericDataType),
)

_UDAF_TYPES: Mapping[DataType, str] = {
    **dict.fromkeys(_NUMERIC_ARRAY_DATA_TYPES, I_VECTOR),
    **{data_type: data_type for data_type in _NUMERIC_DATA_TYPES},
    STRING: "Object",
    LOCAL_DATE: "Object",
    LOCAL_DATE_TIME: "Object",
    LOCAL_TIME: "Long",
    ZONED_DATE_TIME: "Object",
}


_TYPE_CONSTRAINTS: Mapping[DataType, Collection[DataType]] = {
    **{
        data_type: _NUMERIC_DATA_TYPES[index:]
        for index, data_type in enumerate(_NUMERIC_DATA_TYPES)
    },
    **{data_type: [data_type] for data_type in _NUMERIC_ARRAY_DATA_TYPES},
    "Object": [
        "Object",
        STRING,
        LOCAL_DATE,
        LOCAL_TIME,
        LOCAL_DATE_TIME,
        ZONED_DATE_TIME,
    ],
}


@final
@dataclass(frozen=True, eq=False, kw_only=True)
class AppliedJavaFunctionOperation(JavaFunctionOperation):
    _underlyings: Sequence[Operation]
    _java_function: JavaFunction

    @property
    @override
    def java_function(self) -> JavaFunction:
        return self._java_function

    @property
    @override
    def underlyings(self) -> Sequence[Operation]:
        return self._underlyings


def _to_operation(value: object, /) -> Operation:
    if isinstance(value, Operation):
        return value

    if isinstance(value, MeasureDefinition):
        raise TypeError(
            f"`{type(value).__name__}` cannot be converted to an `{Operation.__name__}`.",
        )

    from ..column import Column  # pylint: disable=nested-import

    if isinstance(value, Column):
        return ColumnOperation(value._identifier, value.data_type)

    return ConstantOperation(
        value,  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    )


class JavaFunction(ABC):
    @abstractmethod
    def add_method_source_codes(self, method_codes: set[str]) -> None:
        """Adds the source code of methods to be declared in the compiled Java class."""

    @abstractmethod
    def update_class_imports(self, additional_imports: set[str]) -> None:
        """Updates the class's imports with the requirements for this function."""

    @abstractmethod
    def get_output_type_function(
        self,
    ) -> Callable[[Collection[JavaOperationElement], Py4jClient], DataType]:
        """Get the output type of the function."""

    def __call__(self, *values: object) -> JavaFunctionOperation:
        """Apply this function to the passed values."""
        operations = [_to_operation(value) for value in values]
        return AppliedJavaFunctionOperation(
            _underlyings=operations,
            _java_function=self,
        )

    @abstractmethod
    def get_java_source_code(
        self,
        *operation_elements: JavaOperationElement,
        py4j_client: Py4jClient,
    ) -> str:
        """Generate and return the Java source code which calls this function on the passed operation elements."""


@final
class CustomJavaFunction(JavaFunction):
    """A custom Java function which can be applied to constants, columns or operations."""

    def __init__(
        self,
        *signatures: Sequence[tuple[str, DataType]],
        method_name: str,
        method_body: str,
        output_type: DataType,
        additional_imports: set[str] | None = None,
    ):
        """Creates a new JavaFunction.

        Args:
            signatures: Sequence of tuples containing the variable name and type, used to declare the method.
            method_name: The name of the method, this should be unique.
            method_body: The java code to be executed inside the method.
            output_type: The data type of the output.
            additional_imports: Java packages which need importing for the function to work.
        """
        self.inputs: Final = signatures
        self.signatures: Final[Sequence[Sequence[DataType]]] = tuple(
            tuple(data_type for _, data_type in signature) for signature in signatures
        )
        self.method_name: Final = f"{method_name}{round(time())}"
        self.method_body: Final = method_body
        self.output_type: Final = output_type
        self.additional_imports: Final = additional_imports

    @override
    def update_class_imports(self, additional_imports: set[str]) -> None:
        if self.additional_imports is not None:
            additional_imports.update(self.additional_imports)

    @override
    def add_method_source_codes(self, method_codes: set[str]) -> None:
        method_implementations = [
            self._get_java_method_code(signature) for signature in self.inputs
        ]
        method_codes.update(method_implementations)

    @override
    def get_output_type_function(
        self,
    ) -> Callable[[Collection[JavaOperationElement], Py4jClient], DataType]:
        def output_type(
            _ignored: Collection[JavaOperationElement],
            _py4j_client: Py4jClient,
        ) -> DataType:
            return self.output_type

        return output_type

    def _get_java_method_code(
        self,
        selected_signature: Sequence[tuple[str, DataType]],
    ) -> str:
        inputs = [
            f"{_UDAF_TYPES[_input[1]]} {_input[0]}" for _input in selected_signature
        ]
        input_string = ",".join(inputs)
        return _METHOD_TEMPLATE.format(
            input_string=input_string,
            method_body=self.method_body,
            method_name=self.method_name,
            output_type=_UDAF_TYPES[self.output_type],
        )

    @override
    def get_java_source_code(
        self,
        *operation_elements: JavaOperationElement,
        py4j_client: Py4jClient,
    ) -> str:
        can_call = _is_signature_valid(self.signatures, operation_elements)
        if not can_call:
            raise ValueError(
                "Couldn't find any compatible signatures for this function.",
            )
        operation_strings = [
            operation.get_java_source_code() for operation in operation_elements
        ]
        parameter_string = ",".join(operation_strings)
        return f"{self.method_name}({parameter_string})"


@final
@dataclass(frozen=True, kw_only=True)
class ExistingJavaFunction(JavaFunction):
    """Function used to call static Java methods.

    Args:
        method_call_string: The string to be used to call the method without the brackets. e.g: "Math.sum"
        import_package: Package to be imported to make the method accessible.
    """

    method_call_string: str
    import_package: str | None = None

    @override
    def get_java_source_code(
        self,
        *operation_elements: JavaOperationElement,
        py4j_client: Py4jClient,
    ) -> str:
        signatures = self._get_signature_from_java(py4j_client)
        can_call = _is_signature_valid(signatures, operation_elements)

        if not can_call:
            raise ValueError("No compatible signatures found for this method.")

        operation_strings = ",".join(
            operationElement.get_java_source_code()
            for operationElement in operation_elements
        )

        return f"{self.method_call_string}({operation_strings})"

    def _get_signature_from_java(self, py4j_client: Py4jClient) -> list[list[DataType]]:
        """Get the method's signature from the JVM."""
        components = self.method_call_string.split(".")
        clazz = components[0]
        method_name = components[1]
        full_class = f"{self.import_package}.{clazz}"
        java_signatures = py4j_client.jvm.io.atoti.runtime.internal.udaf.util.UdafCompiler.getMethodSignatures(
            full_class,
            method_name,
        )
        parsed_signatures: list[list[DataType]] = []
        for java_signature in to_python_list(java_signatures):
            python_signature = to_python_list(java_signature)
            if I_VECTOR in python_signature:
                parsed_signatures.extend(
                    [
                        (
                            parse_data_type(argument)
                            if argument != I_VECTOR
                            else array_type
                        )
                        for argument in python_signature
                    ]
                    for array_type in _NUMERIC_ARRAY_DATA_TYPES
                )
            else:
                parsed_signatures.append(
                    [parse_data_type(argument) for argument in python_signature],
                )
        return parsed_signatures

    def _get_output_type_function(
        self,
    ) -> Callable[[Collection[JavaOperationElement], Py4jClient], DataType]:
        components = self.method_call_string.split(".")
        clazz = components[0]
        java_method = components[1]
        java_class = f"{self.import_package}.{clazz}"

        def output_type_function(
            operation_elements: Collection[JavaOperationElement],
            py4j_client: Py4jClient,
        ) -> DataType:
            java_types = [
                _UDAF_TYPES[operation_element.output_type]
                for operation_element in operation_elements
            ]
            java_output_type = _get_output_type_from_java(
                java_class=java_class,
                java_method=java_method,
                types=java_types,
                py4j_client=py4j_client,
            )

            if java_output_type != I_VECTOR:
                return java_output_type

            return _get_arrays_types_widening(
                [
                    operation_element.output_type
                    for operation_element in operation_elements
                    if is_numeric_array_type(operation_element.output_type)
                ],
            )

        return output_type_function

    @override
    def get_output_type_function(
        self,
    ) -> Callable[[Collection[JavaOperationElement], Py4jClient], DataType]:
        return self._get_output_type_function()

    @override
    def update_class_imports(self, additional_imports: set[str]) -> None:
        if self.import_package:
            additional_imports.add(self.import_package)

    @override
    def add_method_source_codes(self, method_codes: set[str]) -> None: ...


def _get_arrays_types_widening(
    arrays_types: Collection[NumericArrayDataType],
    /,
) -> NumericArrayDataType:
    # Pyright thinks that the return type is just `str`.
    return next(  # pyright: ignore[reportReturnType]
        (
            array_type
            for array_type in _NUMERIC_ARRAY_DATA_TYPES
            if array_type in arrays_types
        ),
        _NUMERIC_ARRAY_DATA_TYPES[0],
    )


def _is_signature_valid(
    signatures: Collection[Collection[DataType]],
    operation_elements: Collection[JavaOperationElement],
) -> bool:
    """Ensure that the operations' types are compatible with at least one signature."""
    return any(
        all(
            operationElement.output_type in _TYPE_CONSTRAINTS.get(input_type, [])
            for operationElement, input_type in zip(
                operation_elements,
                signature,
                strict=True,
            )
        )
        for signature in signatures
        if len(signature) == len(operation_elements)
    )


def _get_output_type_from_java(
    *,
    java_class: str,
    java_method: str,
    types: Collection[str],
    py4j_client: Py4jClient,
) -> Literal[DataType, IVectorType]:
    java_types = ListConverter().convert(types, py4j_client.gateway._gateway_client)
    output_type: str = py4j_client.jvm.io.atoti.runtime.internal.udaf.util.UdafCompiler.getMethodOutputType(
        java_class,
        java_method,
        java_types,
    )
    return I_VECTOR if output_type == I_VECTOR else parse_data_type(output_type)
