from typing import Annotated, TypeAlias

from pydantic import Field

UserName: TypeAlias = Annotated[str, Field(min_length=1)]
