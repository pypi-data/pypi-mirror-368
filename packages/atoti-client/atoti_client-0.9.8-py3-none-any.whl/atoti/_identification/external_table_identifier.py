from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .external_table_catalog_name import ExternalTableCatalogName
from .external_table_schema_name import ExternalTableSchemaName
from .identifier import Identifier
from .table_name import TableName


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True, order=True)
class ExternalTableIdentifier(Identifier):
    """The identifier of a :class:`~atoti.ExternalTable` in the context of a :class:`~atoti.ExternalDatabaseConnection`."""

    catalog_name: ExternalTableCatalogName
    schema_name: ExternalTableSchemaName
    table_name: TableName
    _: KW_ONLY

    @override
    def __repr__(self) -> str:
        parts = (
            (self.catalog_name, self.schema_name, self.table_name)
            if self.catalog_name
            else (self.schema_name, self.table_name)
        )
        return f"t[{', '.join(repr(part) for part in parts)}]"
