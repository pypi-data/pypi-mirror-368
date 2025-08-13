from typing import Annotated, TypeAlias

from pydantic import Field

LevelName: TypeAlias = Annotated[str, Field(min_length=1)]
