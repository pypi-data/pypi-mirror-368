from .._client import Client
from .._client._get_json_response_body_type_adapter import (
    get_json_response_body_type_adapter,
)
from .discovery import Discovery


def get_discovery(*, client: Client) -> Discovery:
    path = f"{client.get_path_and_version_id('activeviam/pivot')[0]}/cube/discovery"
    response = client._http_client.get(path).raise_for_status()
    body = response.content
    return get_json_response_body_type_adapter(Discovery).validate_json(body)
