from typing import Annotated, TypeAlias

from pydantic import Field

ApplicationName: TypeAlias = Annotated[str, Field(min_length=1)]
