from collections.abc import Collection
from typing import Protocol

from ._data_type import DataType
from ._identification import IdentifierT_co


class GetDataTypes(Protocol):
    def __call__(
        self,
        identifiers: Collection[IdentifierT_co],
        /,
        *,
        cube_name: str,
    ) -> dict[IdentifierT_co, DataType]: ...
