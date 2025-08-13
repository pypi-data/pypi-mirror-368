from typing import Annotated, TypeAlias

from pydantic import Field

ExternalTableSchemaName: TypeAlias = Annotated[str, Field(min_length=1)]
"""The name of the schema in which the external table is.

In BigQuery this is called "dataset" and in ClickHouse "database".
"""
