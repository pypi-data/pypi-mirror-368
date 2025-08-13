from typing import Annotated, TypeAlias

from pydantic import Field

QueryCubeName: TypeAlias = Annotated[str, Field(min_length=1)]
