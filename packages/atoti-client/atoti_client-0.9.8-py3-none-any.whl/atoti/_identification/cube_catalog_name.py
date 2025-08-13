from typing import Annotated, TypeAlias

from pydantic import Field

CubeCatalogName: TypeAlias = Annotated[str, Field(min_length=1)]
