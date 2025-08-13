from typing import final

from pydantic.dataclasses import dataclass

from ._data_type import DataType
from ._identification import ColumnName
from ._pydantic import PYDANTIC_CONFIG


@final
@dataclass(config=PYDANTIC_CONFIG, frozen=True, kw_only=True, order=True)
class ColumnDefinition:
    name: ColumnName
    data_type: DataType
    nullable: bool = False
