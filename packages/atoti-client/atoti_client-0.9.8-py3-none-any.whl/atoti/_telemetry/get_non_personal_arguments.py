from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterable, Mapping, Sized
from dataclasses import dataclass
from inspect import Parameter, signature
from typing import final, get_type_hints

from .._typing import LiteralArg, get_literal_args
from .get_non_personal_type_name import get_non_personal_type_name

_MEANINGLESS_PARAMETERS = ("self", "cls")

_NON_PERSONAL_DATA_TYPES = (bool, int, float, bytes, type(None))


def _get_non_personal_type_name_with_size(value: object, /) -> str:
    return (
        f"""{get_non_personal_type_name(value)}{f"[{len(value)}]" if isinstance(value, Sized) else ""}"""
        if isinstance(value, Iterable) and not isinstance(value, str)  # pylint: disable=no-iterable
        else get_non_personal_type_name(value)
    )


def _get_non_personal_value(value: object, /, *, annotated_type: object) -> str:
    return (
        str(value)
        if isinstance(value, _NON_PERSONAL_DATA_TYPES)
        or (isinstance(value, LiteralArg) and value in get_literal_args(annotated_type))
        else _get_non_personal_type_name_with_size(value)
    )


@final
@dataclass(frozen=True, kw_only=True)
class FunctionParameter:
    annotated_type: object | None = None


@final
@dataclass(frozen=True, kw_only=True)
class FunctionParameters:
    positional_parameters: Mapping[str, FunctionParameter]
    variadic_positional_parameter: tuple[str, FunctionParameter] | None
    keyword_only_parameters: Mapping[str, FunctionParameter]


def _get_function_parameters(
    function: Callable[..., object],
    /,
) -> FunctionParameters:
    type_hints: Mapping[str, object] = {}

    with contextlib.suppress(  # Some parameters have types not resolvable at runtime.
        NameError,
        TypeError,
    ):
        type_hints = get_type_hints(function)

    positional_parameters: dict[str, FunctionParameter] = {}
    variadic_positional_parameter: tuple[str, FunctionParameter] | None = None
    keyword_only_parameters: dict[str, FunctionParameter] = {}

    for parameter in signature(function).parameters.values():
        function_parameter = FunctionParameter(
            annotated_type=type_hints.get(parameter.name),
        )

        if parameter.kind == Parameter.VAR_POSITIONAL.value:
            variadic_positional_parameter = (
                parameter.name,
                function_parameter,
            )
        elif parameter.kind == Parameter.KEYWORD_ONLY.value:
            keyword_only_parameters[parameter.name] = function_parameter
        elif parameter.kind == Parameter.VAR_KEYWORD.value:
            continue
        else:
            positional_parameters[parameter.name] = function_parameter

    return FunctionParameters(
        positional_parameters=positional_parameters,
        variadic_positional_parameter=variadic_positional_parameter,
        keyword_only_parameters=keyword_only_parameters,
    )


_FUNCTION_PARAMETERS_CACHE: dict[str, FunctionParameters] = {}


# Cannot simply decorate `_get_function_parameters` with `functools.cache` as bound functions can be unhashable and thus not valid arguments.
def _get_cached_function_parameters(
    function: Callable[..., object],
    /,
) -> FunctionParameters:
    full_path = f"{function.__module__}.{function.__qualname__}"
    function_parameters = _FUNCTION_PARAMETERS_CACHE.get(full_path)
    if not function_parameters:
        function_parameters = _get_function_parameters(function)
        _FUNCTION_PARAMETERS_CACHE[full_path] = function_parameters
    return function_parameters


def get_non_personal_arguments(
    function: Callable[..., object],
    /,
    *args: object,
    **kwargs: object,
) -> dict[str, str]:
    """Return a mapping from parameter name to non-personal argument value.

    *args* and *kwargs* not matching *function*'s signature will be ignored.
    """
    arguments: dict[str, str] = {}
    function_parameters = _get_cached_function_parameters(function)

    for value, (parameter_name, parameter) in zip(
        args,
        function_parameters.positional_parameters.items(),
        strict=False,
    ):
        if parameter_name in _MEANINGLESS_PARAMETERS:
            continue

        arguments[parameter_name] = _get_non_personal_value(
            value,
            annotated_type=parameter.annotated_type,
        )

    if function_parameters.variadic_positional_parameter:
        arguments[function_parameters.variadic_positional_parameter[0]] = str(
            tuple(
                _get_non_personal_value(
                    variadic_parameter_value,
                    annotated_type=function_parameters.variadic_positional_parameter[
                        1
                    ].annotated_type,
                )
                for variadic_parameter_value in args[
                    len(function_parameters.positional_parameters) :
                ]
            ),
        )

    for parameter_name, value in kwargs.items():
        # This can happen when a positional or keyword argument is passed with a keyword.
        if parameter_name in function_parameters.positional_parameters:
            arguments[parameter_name] = _get_non_personal_value(
                value,
                annotated_type=function_parameters.positional_parameters[
                    parameter_name
                ].annotated_type,
            )
        elif parameter_name in function_parameters.keyword_only_parameters:
            arguments[parameter_name] = _get_non_personal_value(
                value,
                annotated_type=function_parameters.keyword_only_parameters[
                    parameter_name
                ].annotated_type,
            )
        else:
            # Unknown keyword argument.
            continue

    return arguments
