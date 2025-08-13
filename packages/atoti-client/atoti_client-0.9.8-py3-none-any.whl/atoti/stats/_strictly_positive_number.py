from typing import Annotated, TypeAlias

from pydantic import Field

StrictlyPositiveNumber: TypeAlias = Annotated[int | float, Field(gt=0)]
