from .._cellset import CellSet
from .._client import Client
from .._client._get_json_response_body_type_adapter import (
    get_json_response_body_type_adapter,
)
from .context import Context


def execute_query_to_cellset(
    mdx: str, /, *, client: Client, context: Context
) -> CellSet:
    path = f"{client.get_path_and_version_id('activeviam/pivot')[0]}/cube/query/mdx"
    response = client._http_client.post(
        path, json={"context": {**context}, "mdx": mdx}
    ).raise_for_status()
    body = response.content
    return get_json_response_body_type_adapter(CellSet).validate_json(
        body,
    )
