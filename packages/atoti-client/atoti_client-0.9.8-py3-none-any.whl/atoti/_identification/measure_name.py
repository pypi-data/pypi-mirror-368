from typing import Annotated, TypeAlias

from pydantic import AfterValidator


def _validate(name: str, /) -> str:
    if not name:
        raise ValueError("Empty strings are not allowed.")

    if "," in name:
        raise ValueError(f"`,` is not allowed, got `{name}`.")

    if name != name.strip():
        raise ValueError(
            f"Leading or trailing whitespaces are not allowed, got `{name}`.",
        )

    return name


MeasureName: TypeAlias = Annotated[str, AfterValidator(_validate)]
