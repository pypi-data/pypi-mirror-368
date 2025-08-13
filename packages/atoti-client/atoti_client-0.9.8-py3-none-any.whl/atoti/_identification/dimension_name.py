from typing import Annotated, TypeAlias

from pydantic import Field

DimensionName: TypeAlias = Annotated[str, Field(min_length=1)]
