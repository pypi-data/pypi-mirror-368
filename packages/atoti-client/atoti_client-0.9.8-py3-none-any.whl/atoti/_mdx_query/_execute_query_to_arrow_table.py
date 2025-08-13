from typing import Final, final

import httpx
import pyarrow as pa

from .._client import Client
from .context import Context


# Adapted from https://github.com/encode/httpx/discussions/2296#discussioncomment-6781355.
@final
class _FileLikeAdapter:
    def __init__(self, response: httpx.Response, /):
        self._response: Final = response
        self._iterator: Final = response.iter_raw()
        self._buffer = bytearray()
        self._buffer_offset = 0

    @property
    def closed(self) -> bool:
        return self._response.is_closed

    def read(self, size: int = -1) -> bytearray | bytes:
        while len(self._buffer) - self._buffer_offset < size:
            try:
                chunk = next(self._iterator)
                self._buffer += chunk
            except StopIteration:  # noqa: PERF203
                break

        if len(self._buffer) - self._buffer_offset >= size:
            data = self._buffer[self._buffer_offset : self._buffer_offset + size]
            self._buffer_offset += size
            return data

        data = self._buffer[self._buffer_offset :]
        self._buffer.clear()
        self._buffer_offset = 0
        return data


def execute_query_to_arrow_table(  # pyright: ignore[reportUnknownParameterType]
    mdx: str, /, *, client: Client, context: Context
) -> pa.Table:
    path = f"{client.get_path_and_version_id('activeviam/pivot')[0]}/cube/dataexport/download"
    with client._http_client.stream(
        "POST",
        path,
        json={
            "jsonMdxQuery": {"context": context, "mdx": mdx},
            "outputConfiguration": {"format": "arrow"},
        },
    ) as response:
        response.raise_for_status()
        source = _FileLikeAdapter(response)
        record_batch_stream = pa.ipc.open_stream(source)
        schema = record_batch_stream.schema
        for name in schema.names:
            schema.field(name).with_nullable(True)  # noqa: FBT003
        return pa.Table.from_batches(record_batch_stream, schema=schema)
