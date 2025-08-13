from collections.abc import Set as AbstractSet
from typing import Annotated, TypeAlias

from pydantic import Field

from .cube_catalog_name import CubeCatalogName

CubeCatalogNames: TypeAlias = Annotated[
    AbstractSet[CubeCatalogName], Field(max_length=1)
]
