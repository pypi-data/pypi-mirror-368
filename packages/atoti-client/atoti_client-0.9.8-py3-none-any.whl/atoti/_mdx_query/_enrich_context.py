from math import ceil

from .._typing import Duration
from .context import Context


def enrich_context(context: Context, /, *, timeout: Duration) -> Context:
    return {"queriesTimeLimit": ceil(timeout.total_seconds()), **context}
