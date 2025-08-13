from typing import Annotated, TypeAlias

from pydantic import Field

ColumnName: TypeAlias = Annotated[str, Field(min_length=1)]
