from typing import (
    TypeVar,
    get_args,  # noqa: TID251
    get_origin,
)


def _get_type_var_args(
    _type: type,
    /,
    *,
    parent_args: tuple[object, ...],
    type_var_args: dict[TypeVar, object],
) -> None:
    bases = getattr(_type, "__orig_bases__", None)

    if not bases:
        return

    for base in bases:
        base_origin = get_origin(base)
        base_args = get_args(base)
        base_type_vars = [arg for arg in base_args if isinstance(arg, TypeVar)]

        for type_var, parent_arg in zip(base_type_vars, parent_args, strict=False):
            if type_var not in type_var_args:
                type_var_args[type_var] = parent_arg

        _get_type_var_args(
            base_origin, parent_args=base_args, type_var_args=type_var_args
        )

    return


def get_type_var_args(_type: type, /) -> dict[TypeVar, object]:
    type_var_args: dict[TypeVar, object] = {}
    _get_type_var_args(_type, parent_args=(), type_var_args=type_var_args)
    return type_var_args
