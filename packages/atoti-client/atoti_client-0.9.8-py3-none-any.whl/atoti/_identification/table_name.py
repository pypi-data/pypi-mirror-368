from typing import Annotated, TypeAlias

from pydantic import Field

TableName: TypeAlias = Annotated[str, Field(min_length=1)]
