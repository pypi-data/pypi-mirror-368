from typing import Annotated, TypeAlias

from pydantic import Field

HierarchyName: TypeAlias = Annotated[str, Field(min_length=1)]
