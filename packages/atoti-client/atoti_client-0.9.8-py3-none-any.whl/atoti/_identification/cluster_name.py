from typing import Annotated, TypeAlias

from pydantic import Field

ClusterName: TypeAlias = Annotated[str, Field(min_length=1)]
