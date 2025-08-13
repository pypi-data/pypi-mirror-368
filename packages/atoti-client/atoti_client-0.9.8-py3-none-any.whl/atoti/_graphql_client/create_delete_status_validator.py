from collections.abc import Callable
from typing import TypeAlias, TypeVar

from .enums import DeleteStatus

_Key: TypeAlias = str | tuple[str, ...]

def validate_delete_status(status: DeleteStatus, /, *, key: _Key) -> None:
    match status:
        case DeleteStatus.DELETED:
            return
        case DeleteStatus.NOT_FOUND:
            raise KeyError(key)

_O = TypeVar("_O")

def create_delete_status_validator(
    key: _Key,
    get_delete_status: Callable[[_O], DeleteStatus],
    /,
) -> Callable[[_O], None]:
    return lambda output: validate_delete_status(get_delete_status(output), key=key)
