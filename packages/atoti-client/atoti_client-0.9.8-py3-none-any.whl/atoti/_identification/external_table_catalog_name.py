from typing import TypeAlias

ExternalTableCatalogName: TypeAlias = str
"""The name of the catalog in which the external table is.

Some databases call this "database", BigQuery calls it "project ID".
In ClickHouse, this is is not used so it will be ``""``.
"""
