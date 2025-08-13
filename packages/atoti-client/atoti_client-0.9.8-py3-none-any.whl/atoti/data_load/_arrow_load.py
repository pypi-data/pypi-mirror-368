from dataclasses import KW_ONLY
from pathlib import Path
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .data_load import DataLoad


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ArrowLoad(DataLoad):
    path: Path
    _: KW_ONLY

    @property
    @override
    def _options(self) -> dict[str, object]:
        return {"absolutePath": str(self.path)}

    @property
    @override
    def _plugin_key(self) -> str:
        return "ARROW"
