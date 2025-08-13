from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, kw_only=True)
class ExternalAggregateTableSql:
    create: str
    insert: str
