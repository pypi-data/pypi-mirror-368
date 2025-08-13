from typing import final

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG


@final
@dataclass(config=PYDANTIC_CONFIG, frozen=True, kw_only=True)
class NotebookCell:
    has_built_widget: bool
    id: str
