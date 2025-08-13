from typing import Annotated, TypeVar

from pydantic import BeforeValidator, TypeAdapter

from .._pydantic import get_type_adapter


def _normalize_json_response_body(value: object, /) -> object:
    return (
        value.get("data")  # Atoti Server < 6.0.0-M1.
        if isinstance(value, dict) and value.get("status") == "success"
        else value
    )


_BodyT = TypeVar("_BodyT")


# Remove when dropping support for Atoti Server < 6.0.0-M1.
def get_json_response_body_type_adapter(
    body_type: type[_BodyT],
    /,
) -> TypeAdapter[_BodyT]:
    return get_type_adapter(
        Annotated[  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
            body_type,
            BeforeValidator(_normalize_json_response_body),
        ],
    )
