from __future__ import annotations

import ssl
from collections.abc import Callable, Generator, Mapping, Sequence, Set as AbstractSet
from contextlib import contextmanager
from functools import cached_property
from mimetypes import types_map as _types_map
from pathlib import Path
from typing import Annotated, Final, Literal, TypeAlias, final, overload

import httpx
from pydantic import BeforeValidator, ConfigDict, TypeAdapter
from pydantic.dataclasses import dataclass

from .._collections import FrozenSequence
from .._content_client import ContentClient
from .._content_client.content_client import _API_NAME as _CONTENT_API_NAME
from .._doc import doc
from .._experimental import experimental
from .._graphql_client import GraphqlClient
from .._py4j_client import Py4jClient
from .._pydantic import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    create_camel_case_alias_generator,
    get_type_adapter,
)
from ..authentication import Authenticate, ClientCertificate
from ._get_path_and_version_id import (
    PathType,
    VersionIdT_co,
    get_path_and_version_id,
)
from ._get_server_versions import get_server_versions
from ._has_compatible_standard_runtime_api import has_compatible_standard_runtime_api
from ._ping import ping as _ping
from ._require_live_extension import require_live_extension
from ._server_versions import ServerVersions

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}

_GetDataModelTransactionId: TypeAlias = Callable[[], str | None]


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class _ErrorChainItem:
    message: str
    type: str


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class _ConciseJsonResponseErrorBody:
    error: str
    path: str
    status: int


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class _DetailedJsonResponseErrorBody:
    error_chain: FrozenSequence[_ErrorChainItem]
    stack_trace: str


_JsonResponseErrorBody = _ConciseJsonResponseErrorBody | _DetailedJsonResponseErrorBody


def _normalize_http_error_body(value: object, /) -> object:
    return (
        value.get("error")  # Atoti Server < 6.0.0-M1.
        if isinstance(value, dict) and value.get("status") == "error"
        else value
    )


def _enhance_json_response_raise_for_status(response: httpx.Response, /) -> None:
    if (
        response.is_success
        or response.headers.get("Content-Type") != _types_map[".json"]
    ):
        return

    original_raise_for_status = response.raise_for_status

    def _enhanced_json_response_raise_for_status() -> httpx.Response:
        try:
            return original_raise_for_status()
        except httpx.HTTPStatusError as error:
            adapter: TypeAdapter[_JsonResponseErrorBody] = get_type_adapter(
                _ConciseJsonResponseErrorBody
                | Annotated[  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
                    _DetailedJsonResponseErrorBody,
                    # Remove when dropping support for Atoti Server < 6.0.0-M1.
                    BeforeValidator(_normalize_http_error_body),
                ],
            )
            body_json = response.read()
            body = adapter.validate_json(body_json)
            message = (
                body.stack_trace
                if isinstance(body, _DetailedJsonResponseErrorBody)
                else body.error
            )
            args = (message,)
            assert len(error.args) == len(args), (  # noqa: PT017
                "The args' format changed, make sure nothing interesting is getting overridden."
            )
            error.args = args
            raise

    response.raise_for_status = _enhanced_json_response_raise_for_status  # type: ignore[method-assign]


def _remove_cookies(request: httpx.Request, /) -> None:
    request.headers.pop("Cookie", None)


@final
class Client:
    """Low-level client to communicate with Atoti Server."""

    @contextmanager
    @staticmethod
    def _create(
        url: str,
        /,
        *,
        authentication: Authenticate | ClientCertificate | None,
        certificate_authority: Path | None,
        get_data_model_transaction_id: _GetDataModelTransactionId,
        # Remove this parameter and always consider it `True` once `QuerySession`s can be pinged before the first `QueryCube` creation.
        ping: bool = True,
        py4j_client: Py4jClient | None,
    ) -> Generator[Client, None, None]:
        authenticate: Authenticate | None = None

        auth: Callable[[httpx.Request], httpx.Request] | None = None
        verify: ssl.SSLContext | Literal[True] = True

        if certificate_authority is not None:
            verify = ssl.create_default_context(cafile=certificate_authority)

        match authentication:
            case None:
                ...
            case ClientCertificate():
                if not isinstance(verify, ssl.SSLContext):
                    verify = ssl.create_default_context()

                verify.load_cert_chain(
                    certfile=authentication.certificate,
                    keyfile=authentication.keyfile,
                    password=authentication.password,
                )

                def _authenticate(_: str, /) -> Mapping[str, str]:
                    raise RuntimeError(
                        "Cannot generate authentication headers from client certificate.",
                    )

                authenticate = _authenticate
            case _:

                def _auth(request: httpx.Request, /) -> httpx.Request:
                    headers = authentication(str(request.url))
                    request.headers.update(headers)
                    return request

                auth = _auth
                authenticate = authentication

        with httpx.Client(
            auth=auth,
            base_url=url,
            event_hooks={
                "request": [
                    # To make the client stateless.
                    # See https://github.com/encode/httpx/issues/2992.
                    _remove_cookies,
                ],
                "response": [
                    _enhance_json_response_raise_for_status,
                ],
            },
            verify=verify,
            timeout=None,
        ) as http_client:
            server_versions = get_server_versions(http_client=http_client)

            client = Client(
                authenticate=authenticate,
                get_data_model_transaction_id=get_data_model_transaction_id,
                http_client=http_client,
                py4j_client=py4j_client,
                server_versions=server_versions,
            )

            if ping:
                # The `ping` endpoint is protected.
                # Calling it ensures that the client can authenticate against the server.
                _ping(
                    "activeviam/pivot",
                    http_client=http_client,
                    server_versions=server_versions,
                )

            yield client

    def __init__(
        self,
        *,
        authenticate: Authenticate | None,
        get_data_model_transaction_id: _GetDataModelTransactionId,
        http_client: httpx.Client,
        py4j_client: Py4jClient | None,
        server_versions: ServerVersions,
    ) -> None:
        """Private constructor, retrieve the client from :class:`~atoti.Session` instead.

        :meta private:
        """
        self._authenticate: Final = authenticate
        self._get_data_model_transaction_id: Final = get_data_model_transaction_id
        self._http_client: Final = http_client
        self._py4j_client: Final = py4j_client
        self._server_versions: Final = server_versions

    @cached_property
    def _content_client(self) -> ContentClient | None:
        return (
            ContentClient(
                http_client=self._http_client,
                server_versions=self._server_versions,
            )
            if _CONTENT_API_NAME in self._server_versions.apis
            else None
        )

    @overload
    def get_path_and_version_id(
        self,
        api_name: str,
        /,
        *,
        denied_version_ids: AbstractSet[str] = ...,
        path_type: PathType = ...,
    ) -> tuple[str, str]: ...

    @overload
    def get_path_and_version_id(
        self,
        api_name: str,
        /,
        *,
        allowed_version_ids: Sequence[VersionIdT_co],
        denied_version_ids: AbstractSet[str] = ...,
        path_type: PathType = ...,
    ) -> tuple[str, VersionIdT_co]: ...

    def get_path_and_version_id(
        self,
        api_name: str,
        /,
        *,
        allowed_version_ids: Sequence[str] | None = None,
        denied_version_ids: AbstractSet[str] = frozenset(),
        path_type: PathType = "rest",
    ) -> tuple[str, str]:
        """Return the matching ``(path, version_id)``.

        If *allowed_version_ids* is not ``None``, the server versions will be iterated following the order of its elements.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")
                >>> client = session._client

            >>> client.get_path_and_version_id("activeviam/pivot")
            ('activeviam/pivot/rest/v10', '10')
            >>> client.get_path_and_version_id("activeviam/pivot", path_type="ws")
            ('activeviam/pivot/ws/v9', '9')
            >>> client.get_path_and_version_id(
            ...     "activeviam/pivot", allowed_version_ids=["8", "7"]
            ... )
            Traceback (most recent call last):
              ...
            RuntimeError: None of the allowed version IDs ['8', '7'] match the provided ones: ['9', '10'].
            >>> client.get_path_and_version_id(
            ...     "activeviam/pivot", denied_version_ids={"9", "10", "11"}
            ... )
            Traceback (most recent call last):
              ...
            RuntimeError: No `activeviam/pivot` API with `rest` path found.

        See Also:
            :attr:`http_client` for an example of how this method can be used.

        """
        return get_path_and_version_id(
            api_name,
            path_type=path_type,
            allowed_version_ids=allowed_version_ids,
            denied_version_ids=denied_version_ids,
            server_versions=self._server_versions,
        )

    @cached_property
    def _graphql_client(self) -> GraphqlClient | None:
        if not has_compatible_standard_runtime_api(self._server_versions):
            return None

        return GraphqlClient(
            get_data_model_transaction_id=self._get_data_model_transaction_id,
            http_client=self._http_client,
        )

    @property
    @doc()
    @experimental()
    def http_client(self) -> httpx.Client:
        """The `httpx.Client <https://www.python-httpx.org/api/#client>`__ to communicate with Atoti Server.

        Warning:
            {experimental_feature}

            This is marked as experimental not because it may be renamed or removed but to accommodate the potential replacement of **httpx** with another third-party library in the future.

        Tip:
            It is recommended to use this client instead of reimplementing Atoti Server specific concerns like authentication and error handling with another library such as **AIOHTTP** or **requests**.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")
                >>> client = session._client

            >>> with tt.experimental({{"Client.http_client"}}):
            ...     http_client = client.http_client

            Pinging the server:

            >>> path = f"{{client.get_path_and_version_id('activeviam/pivot')[0]}}/ping"
            >>> path
            'activeviam/pivot/rest/v10/ping'
            >>> http_client.get(path).raise_for_status().text
            'pong'

            If the server returns an error as a JSON response containing a stack trace, the raised Python exception's message will be set to that stack trace:

            >>> path = f"{{client.get_path_and_version_id('activeviam/pivot')[0]}}/cube/query/mdx"
            >>> response = http_client.post(path, json={{"mdx": "Some invalid MDX"}})
            >>> response.raise_for_status()  # doctest: +ELLIPSIS
            Traceback (most recent call last):
              ...
            httpx.HTTPStatusError: com.activeviam.tech.core.api.exceptions.service.BadArgumentException: [400] The provided MDX query is invalid.
            ...
            Caused by: ...: Some invalid MDX
            ...
            Caused by: ...: Parser failure: ...
            >>> sorted(response.json().keys())
            ['errorChain', 'stackTrace']

        """
        return self._http_client

    def _require_content_client(self) -> ContentClient:
        return require_live_extension(self._content_client)

    def _require_graphql_client(self) -> GraphqlClient:
        return require_live_extension(self._graphql_client)

    def _require_py4j_client(self) -> Py4jClient:
        return require_live_extension(self._py4j_client)

    @cached_property
    def _url(self) -> str:
        return str(self._http_client.base_url).rstrip("/")
