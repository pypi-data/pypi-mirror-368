from typing import TypeAlias

from .external_table_catalog_name import ExternalTableCatalogName
from .external_table_schema_name import ExternalTableSchemaName
from .table_name import TableName

ExternalTableKey: TypeAlias = (
    TableName
    | tuple[ExternalTableSchemaName, TableName]
    | tuple[ExternalTableCatalogName, ExternalTableSchemaName, TableName]
)
