from __future__ import annotations

from typing import Literal, cast

from .._typing import get_literal_args

IVectorType = Literal["IVector"]


def _get_i_vector() -> IVectorType:
    arg, *unexpected_args = cast(tuple[IVectorType, ...], get_literal_args(IVectorType))

    assert not unexpected_args, (
        f"Expected `IVectorType` to have a single arg but has: {len(unexpected_args) + 1}."
    )

    return arg


I_VECTOR = _get_i_vector()
