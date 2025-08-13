from typing import Final, final

from ._client import Client
from ._graphql_client import UpdateProxyInput


@final
class Proxy:
    """The proxy alllowing to forward requests from Atoti Server to another server.

    A request made to ``f"{session.url}/proxy/some/path?foo=bar"`` will be proxied to ``f"{session.proxy.url}/some/path?foo=bar"``:

    The new request will have an :guilabel:`Authorization` HTTP header containing a JWT.
    This JWT contains the following claims:

    * ``sub``: The name of the user making the request to the proxy.
    * ``authorities``: The list of roles of the user.

    This JWT is signed by Atoti Server, except when using the :doc:`community edition </guides/unlocking_all_features>`.

    Warning:
        For maximal flexibility, ``f"{session.url}/proxy"`` does not require authentication.
        It is the responsibility of the server based at :attr:`url` to handle authentication and authorization if needed.

    .. raw:: html

        <div class="mermaid">
        sequenceDiagram
          participant C as Client
          participant S as Atoti Server<br>https://example.com:1337
          participant P as Proxy target server<br>https://custom.com:1991
          C->>S: session.proxy.url = "https://custom.com:1991"
          C->>S: POST /proxy/some/path?foo=bar
          S->>P: POST /some/path?foo=bar<br>with extra HTTP headers:<br>• Authorization: Bearer $jwt<br>• X-Forwarded-Proto: https<br>• X-Forwarded-Host: example.com:1337
          P->>P: ⚠ Check $jwt
          P->>S: HTTP $status_code response
          S->>C: HTTP $status_code response
        </div>

    Example:

        .. doctest::
            :hide:

            >>> jwt_directory = TEST_RESOURCES_PATH / "config" / "jwt"
            >>> session = getfixture("default_session")

        Using a custom JWT key pair to be able to verify JWT signatures in the local server below:

        >>> public_key, public_key_pem, private_key = (
        ...     (jwt_directory / filename).read_text()
        ...     for filename in ["public-key.txt", "public-key.pem", "private-key.txt"]
        ... )

        >>> from jwt import decode
        >>> def get_user(jwt: str, /) -> tuple[str, list[str]]:
        ...     \"\"\"Check the JWT signature and return the user name and roles claims.
        ...
        ...     Verifying the JWT signature is primordial to ensure
        ...     that the request is legitimate and coming from Atoti Server.
        ...
        ...     This function does not rely on Atoti Python SDK
        ...     and could actually be implemented in any language.
        ...     \"\"\"
        ...     claims = decode(jwt, algorithms=["RS512"], key=public_key_pem)
        ...     user_name = claims["sub"]
        ...     user_roles = claims["authorities"]
        ...     return user_name, user_roles

        Starting a secured session:

        >>> session_config = tt.SessionConfig(
        ...     security=tt.SecurityConfig(
        ...         jwt=tt.JwtConfig(key_pair=tt.KeyPair(public_key, private_key))
        ...     )
        ... )
        >>> secured_session = tt.Session.start(session_config)

        The proxy is disabled by default:

        >>> import httpx
        >>> print(secured_session.proxy.url)
        None
        >>> response = httpx.get(f"{secured_session.url}/proxy")
        >>> response.status_code
        501
        >>> response.text
        'The proxy is disabled.'

        Starting a local server:

        >>> from json import dumps
        >>> from http import HTTPStatus
        >>> from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        >>> from threading import Thread
        >>> from urllib.parse import parse_qs, urlparse

        >>> class RequestHandler(BaseHTTPRequestHandler):
        ...     def do_GET(self) -> None:
        ...         parse_result = urlparse(self.path)
        ...         match parse_result.path, parse_qs(parse_result.query):
        ...             case "/whoami", {"mode": [mode]}:
        ...                 token_type, jwt = self.headers["Authorization"].split(" ")
        ...                 match mode:
        ...                     case "jwt":
        ...                         # Most projects will want to raise an error if
        ...                         # `ROLE_USER` is not included in `user_roles`.
        ...                         user_name, user_roles = get_user(jwt)
        ...                     case "session":
        ...                         # This server does not have to be aware of the Atoti session URL
        ...                         # since it can be reconstructed from headers passed by the proxy.
        ...                         protocol = self.headers["X-Forwarded-Proto"]
        ...                         host = self.headers["X-Forwarded-Host"]
        ...                         session_url = f"{protocol}://{host}"
        ...                         authentication = tt.TokenAuthentication(
        ...                             jwt, token_type=token_type
        ...                         )
        ...                         try:
        ...                             with tt.Session.connect(
        ...                                 session_url, authentication=authentication
        ...                             ) as session:
        ...                                 user = session.user
        ...                             user_name = user.name
        ...                             user_roles = sorted(user.roles)
        ...                         except Exception:
        ...                             self.send_response_only(HTTPStatus.FORBIDDEN)
        ...                             self.end_headers()
        ...                             return
        ...                     case _:
        ...                         self.send_response_only(HTTPStatus.BAD_REQUEST)
        ...                         self.end_headers()
        ...                         return
        ...                 body = dumps({"name": user_name, "roles": user_roles})
        ...                 self.send_response_only(HTTPStatus.OK)
        ...                 self.end_headers()
        ...                 self.wfile.write(body.encode("utf-8"))
        ...             case _:
        ...                 self.send_response_only(HTTPStatus.NOT_FOUND)
        ...                 self.end_headers()
        ...
        ...     def do_POST(self) -> None:
        ...         content_length = int(self.headers["Content-Length"])
        ...         body = self.rfile.read(content_length)
        ...         self.send_response_only(HTTPStatus.OK)
        ...         # To show that response headers are sent back to the client.
        ...         self.send_header("X-Custom-Header", "lorem ipsum")
        ...         self.end_headers()
        ...         self.wfile.write(body)

        >>> local_server = ThreadingHTTPServer(("localhost", 0), RequestHandler)
        >>> thread = Thread(daemon=True, target=local_server.serve_forever)
        >>> thread.start()

        The server above is implemented in Python but the proxy target can be any HTTP server or even a lambda function in the cloud.

        Configuring the proxy to forward requests to the local server:

        >>> secured_session.proxy.url = f"http://localhost:{local_server.server_port}"

        Calling the proxy without authentication:

        >>> response = httpx.get(f"{secured_session.url}/proxy/whoami?mode=jwt")
        >>> response.status_code
        200
        >>> response.json()
        {'name': 'anonymousUser', 'roles': ['ROLE_ANONYMOUS']}

        Without authentication, :guilabel:`ROLE_USER` is missing and thus :meth:`atoti.Session.connect` will raise an error:

        >>> response = httpx.get(f"{secured_session.url}/proxy/whoami?mode=session")
        >>> response.status_code
        403

        Adding a user to the session and calling the proxy as this user:

        >>> username, password = "Alice", "abcdef123456"
        >>> alice_roles = {"ROLE_USER", "ROLE_WONDERLAND"}
        >>> secured_session.security.individual_roles[username] = alice_roles
        >>> secured_session.security.basic_authentication.credentials[username] = (
        ...     password
        ... )
        >>> response = httpx.get(
        ...     f"{secured_session.url}/proxy/whoami?mode=jwt",
        ...     auth=(username, password),
        ... )
        >>> response.status_code
        200
        >>> response.json()
        {'name': 'Alice', 'roles': ['ROLE_USER', 'ROLE_WONDERLAND']}

        :guilabel:`ROLE_USER` is present so :meth:`atoti.Session.connect` and the access to :attr:`atoti.Session.user` will both succeed:

        >>> response = httpx.get(
        ...     f"{secured_session.url}/proxy/whoami?mode=session",
        ...     auth=(username, password),
        ... )
        >>> response.status_code
        200
        >>> response.json()
        {'name': 'Alice', 'roles': ['ROLE_USER', 'ROLE_WONDERLAND']}

        Trying an unsupported mode:

        >>> response = httpx.get(f"{secured_session.url}/proxy/whoami?mode=invalid")
        >>> response.status_code
        400

        Trying an unhandled path:

        >>> response = httpx.get(f"{secured_session.url}/proxy")
        >>> response.status_code
        404

        Request and response bodies are not limited to strings:

        >>> from secrets import token_bytes
        >>> bytes = token_bytes()
        >>> response = httpx.post(f"{secured_session.url}/proxy", content=bytes)
        >>> response.status_code
        200
        >>> int(response.headers["Content-Length"]) == len(bytes)
        True
        >>> response.content == bytes
        True
        >>> response.headers["X-Custom-Header"]
        'lorem ipsum'

        Disabling the proxy:

        >>> secured_session.proxy.url = None
        >>> httpx.get(f"{secured_session.url}/proxy").status_code
        501

        On a session without security, :meth:`atoti.Session.connect` always succeeds, even for anonymous calls:

        >>> print(session.proxy.url)
        None
        >>> session.proxy.url = f"http://localhost:{local_server.server_port}"
        >>> response = httpx.get(f"{session.url}/proxy/whoami?mode=session")
        >>> response.status_code
        200
        >>> response.json()
        {'name': 'anonymousUser', 'roles': ['ROLE_ADMIN', 'ROLE_ANONYMOUS', 'ROLE_USER']}

        See :attr:`atoti.Session.user` for an explanation of the roles above.

        Stopping the local server:

        >>> local_server.shutdown()
        >>> local_server.server_close()
        >>> thread.join()

        .. doctest::
            :hide:

            >>> del secured_session

    See Also:
        * :meth:`atoti.Session.endpoint`.

    """

    def __init__(self, *, client: Client) -> None:
        self._client: Final = client

    @property
    def url(self) -> str | None:
        """The URL towards which requests are forwarded.

        If ``None``, the proxy is disabled.
        """
        output = self._client._require_graphql_client().get_proxy_url()
        return output.proxy.url

    @url.setter
    def url(self, url: str | None, /) -> None:
        self._client._require_graphql_client().update_proxy(
            input=UpdateProxyInput(url=url)
        )
