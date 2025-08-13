from collections.abc import Set as AbstractSet
from typing import Annotated, TypeAlias

from pydantic import Field

from .application_name import ApplicationName

ApplicationNames: TypeAlias = Annotated[
    AbstractSet[ApplicationName], Field(max_length=1)
]
