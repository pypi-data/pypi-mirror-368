import httpx

from ._get_path_and_version_id import get_path_and_version_id
from ._server_versions import ServerVersions


def ping(
    api_name: str,
    /,
    *,
    http_client: httpx.Client,
    server_versions: ServerVersions,
) -> None:
    path = (
        f"{get_path_and_version_id(api_name, server_versions=server_versions)[0]}/ping"
    )
    response = http_client.get(path).raise_for_status()
    body = response.text
    expected_body = "pong"
    if body != expected_body:
        raise RuntimeError(
            f"Expected response body to be `{expected_body}` but got `{body}`."
        )
