from .._client import Client
from .._typing import Duration
from ._enrich_context import enrich_context
from .context import Context


def explain_query(
    mdx: str, /, *, client: Client, context: Context, timeout: Duration
) -> object:
    path = f"{client.get_path_and_version_id('activeviam/pivot')[0]}/cube/query/mdx/queryplan"
    context = enrich_context(context, timeout=timeout)
    response = client._http_client.post(
        path,
        json={"context": {**context}, "mdx": mdx},
        # The timeout is part of `context` and is managed by the server.
        timeout=None,
    ).raise_for_status()
    return response.json()
