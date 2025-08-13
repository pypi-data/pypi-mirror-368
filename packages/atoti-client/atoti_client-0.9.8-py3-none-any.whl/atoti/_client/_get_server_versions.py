import httpx

from .._pydantic import get_type_adapter
from ._server_versions import ServerVersions


def get_server_versions(
    *,
    http_client: httpx.Client,
) -> ServerVersions:
    versions_response = http_client.get("versions/rest").raise_for_status()
    body = versions_response.content
    return get_type_adapter(ServerVersions).validate_json(body)
