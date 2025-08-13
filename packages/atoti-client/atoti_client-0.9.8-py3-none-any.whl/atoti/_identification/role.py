from typing import Annotated, TypeAlias

from pydantic import Field

Role: TypeAlias = Annotated[str, Field(min_length=1)]
