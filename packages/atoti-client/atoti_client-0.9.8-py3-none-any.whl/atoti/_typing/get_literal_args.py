from enum import Enum
from functools import cache
from typing import (
    Literal,
    TypeAlias,
    Union,
    get_args,  # noqa: TID251
)

# From https://www.python.org/dev/peps/pep-0586/#legal-parameters-for-literal-at-type-check-time
LiteralArg: TypeAlias = bool | bytes | Enum | int | str | None
"""Type of a value that can be used as :class:`typing.Literal` args."""


# Inspired from https://github.com/agronholm/typeguard/blob/de6ab051309ba74a0a27840f8172697c8778ae4f/src/typeguard/__init__.py#L625-L642.
@cache
def get_literal_args(any_type: object, /) -> tuple[LiteralArg, ...]:
    """Extract all the top-level :class:`typing.Literal` args from the passed type.

    This function exists because :func:`typing.get_args` does not support nested :class:`typing.Literal`s.

    *any_type* cannot be an unresolved type, use :func:`typing.get_type_hints` to handle `postponed evaluation of annotations <https://www.python.org/dev/peps/pep-0563/>`__.

    The returned tuple is guaranteed to contain unique values.
    """
    if getattr(any_type, "__origin__", None) not in {Literal, Union}:
        # Ignore nested types.
        return ()

    literal_args: list[LiteralArg] = []

    def add_arg(new_arg: LiteralArg, /) -> None:
        # Using `any` with `is` rather than just `new_arg in literal_args` to distinguish different booleans with other truthy/falsy values.
        # See https://docs.python.org/3.9/reference/expressions.html#membership-test-operations.
        if any(new_arg is arg for arg in literal_args):
            return
        literal_args.append(new_arg)

    for arg in get_args(any_type):
        if getattr(arg, "__origin__", None) is Literal:
            for new_arg in get_literal_args(arg):
                add_arg(new_arg)
        elif isinstance(arg, LiteralArg):
            add_arg(arg)

    return tuple(literal_args)
