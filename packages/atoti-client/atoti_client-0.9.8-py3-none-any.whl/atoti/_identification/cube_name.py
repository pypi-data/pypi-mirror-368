from typing import Annotated, TypeAlias

from pydantic import Field

CubeName: TypeAlias = Annotated[str, Field(min_length=1)]
