from __future__ import annotations

import json
import traceback
from collections import defaultdict
from collections.abc import Callable
from contextlib import AbstractContextManager, ExitStack
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from mimetypes import types_map as _types_map
from threading import Thread
from types import TracebackType
from typing import Any, Final, TypeAlias, final
from urllib.parse import urlparse

import httpx
from pydantic import JsonValue
from typing_extensions import Self, override

from .._client.client import _ConciseJsonResponseErrorBody
from .._graphql_client import GraphqlClient, GraphQLClientError
from .._pydantic import get_type_adapter
from .._reserved_roles import ROLE_ADMIN, ROLE_USER
from ..user import User
from ._http_method import HttpMethod
from ._path_matcher import PathMatcher
from .request import Request

_Callback: TypeAlias = Callable[[Request, User], JsonValue]


@final
@dataclass(frozen=True, kw_only=True)
class _Response:
    status_code: HTTPStatus
    body: object


@final
class _RequestError(Exception):
    def __init__(self, response: _Response):
        super().__init__(response.body)
        self.response: Final = response


@final
class Server(AbstractContextManager["Server"]):
    def __init__(self, *, session_url: str) -> None:
        self.__server: _HttpServer | None = None
        self._exit_stack: Final = ExitStack()
        self._session_url: Final = session_url

    @property
    def url(self) -> str:
        host, port = self._require_server().server_address[:2]
        assert isinstance(host, str)
        return f"http://{host}:{port}"

    def register_endpoint(
        self,
        *,
        http_method: HttpMethod,
        path: str,
        callback: _Callback,
    ) -> None:
        self._require_server().register_endpoint(
            http_method=http_method, path=path, callback=callback
        )

    def start(self) -> bool:
        """Return ``False`` if the server is already running, or start it and return ``True``."""
        if self.__server is not None:
            return False

        self.__enter__()
        return True

    def stop(self) -> None:
        """No-op if the server is not running."""
        self._exit_stack.close()

    def _require_server(self) -> _HttpServer:
        if self.__server is None:
            raise RuntimeError("The server is not running.")
        return self.__server

    @override
    def __enter__(self) -> Self:
        assert self.__server is None, "The server is already running."

        def unset_server() -> None:
            self.__server = None

        self.__server = self._exit_stack.enter_context(
            _HttpServer(
                server_address=("localhost", 0),
                handler_class=_Handler,
                session_url=self._session_url,
            )
        )
        self._exit_stack.callback(unset_server)
        thread = Thread(daemon=True, target=self._require_server().serve_forever)
        thread.start()
        self._exit_stack.callback(thread.join)
        self._exit_stack.callback(self._require_server().shutdown)
        return self

    @override
    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        exception_traceback: TracebackType | None,
    ) -> None:
        self._exit_stack.__exit__(exception_type, exception_value, exception_traceback)


@final
@dataclass(frozen=True, kw_only=True)
class _Endpoint:
    callback: _Callback
    path_matcher: PathMatcher


@final
class _HttpServer(ThreadingHTTPServer):
    def __init__(
        self,
        *,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        session_url: str,
    ):
        super().__init__(server_address, handler_class)
        self._endpoints_from_method: Final[dict[HttpMethod, list[_Endpoint]]] = (
            defaultdict(list)
        )
        self.session_url: Final = session_url

    def register_endpoint(
        self,
        *,
        http_method: HttpMethod,
        path: str,
        callback: _Callback,
    ) -> None:
        path_matcher = PathMatcher("/" + path)
        self._endpoints_from_method[http_method].append(
            _Endpoint(path_matcher=path_matcher, callback=callback)
        )

    def find_endpoint(
        self,
        *,
        http_method: HttpMethod,
        path: str,
    ) -> tuple[_Callback, dict[str, str]] | None:
        for endpoint in self._endpoints_from_method[http_method]:
            result = endpoint.path_matcher.get_parameters(path)
            if result is not None:
                return endpoint.callback, result
        return None


@final
class _Handler(BaseHTTPRequestHandler):
    def do_DELETE(self) -> None:  # noqa: N802
        self._handle_request("DELETE")

    def do_GET(self) -> None:  # noqa: N802
        self._handle_request("GET")

    def do_PATCH(self) -> None:  # noqa: N802
        self._handle_request("PATCH")

    def do_POST(self) -> None:  # noqa: N802
        self._handle_request("POST")

    def do_PUT(self) -> None:  # noqa: N802
        self._handle_request("PUT")

    def _handle_request(self, http_method: HttpMethod, /) -> None:
        is_admin = False

        try:
            user = self._validate_authorization()
            is_admin = ROLE_ADMIN in user.roles
            response_body = self._execute_endpoint_callback(http_method, user)
            response = _Response(status_code=HTTPStatus.OK, body=response_body)
        except _RequestError as error:
            response = error.response
        except Exception as error:  # noqa: BLE001
            response = self._create_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                traceback.format_exc() if is_admin else str(error),
            )

        self.send_response(response.status_code)
        self.send_header("Content-Type", _types_map[".json"])
        self.end_headers()
        body_as_json = get_type_adapter(type(response.body)).dump_json(response.body)
        self.wfile.write(body_as_json)

    def _execute_endpoint_callback(
        self, http_method: HttpMethod, user: User
    ) -> JsonValue:
        path = urlparse(self.path).path
        endpoint = self._server.find_endpoint(http_method=http_method, path=path)

        if endpoint is None:
            raise _RequestError(
                self._create_error_response(
                    HTTPStatus.NOT_FOUND, "No matching endpoint."
                )
            )

        callback, path_parameters = endpoint

        body = self._read_body()
        request = Request(url=self.path, path_parameters=path_parameters, body=body)
        return callback(request, user)

    def _validate_authorization(self) -> User:
        authorization = self.headers.get("Authorization")
        if authorization is None:
            raise _RequestError(
                self._create_error_response(
                    HTTPStatus.UNAUTHORIZED, "Missing Authorization header."
                )
            )

        try:
            with (
                httpx.Client(
                    base_url=self._server.session_url,
                    headers={"Authorization": authorization},
                ) as http_client,
                GraphqlClient(
                    get_data_model_transaction_id=lambda: None,
                    http_client=http_client,
                ) as graphql_client,
            ):
                user = graphql_client.get_current_user().current_user
        except GraphQLClientError as error:
            raise _RequestError(
                self._create_error_response(
                    HTTPStatus.UNAUTHORIZED, f"Access denied: {error}"
                )
            ) from error

        if ROLE_USER not in user.roles:
            raise _RequestError(
                self._create_error_response(
                    HTTPStatus.UNAUTHORIZED, f"Missing {ROLE_USER}."
                )
            )

        return User(name=user.name, roles=set(user.roles))

    def _read_body(self) -> JsonValue | None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if body:
            try:
                parsed_body: JsonValue = json.loads(body)
            except json.JSONDecodeError as error:
                raise _RequestError(
                    self._create_error_response(
                        HTTPStatus.BAD_REQUEST,
                        f"Request body could not be read: {error}",
                    )
                ) from error
            return parsed_body
        return None

    def _create_error_response(
        self, status_code: HTTPStatus, message: str
    ) -> _Response:
        return _Response(
            status_code=status_code,
            body=_ConciseJsonResponseErrorBody(
                error=message,
                path=self.path,
                status=status_code.value,
            ),
        )

    @override
    def log_message(self, format: str, *args: Any) -> None: ...  # Disable logging.

    @property
    def _server(self) -> _HttpServer:
        assert isinstance(self.server, _HttpServer)
        return self.server
