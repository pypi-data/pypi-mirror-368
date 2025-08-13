from __future__ import annotations

from contextlib import AbstractContextManager, ExitStack
from pathlib import Path
from types import TracebackType
from typing import Final, final

from typing_extensions import NotRequired, TypedDict, Unpack, override

from .._session_resources import started_session_resources
from ..config import SessionConfig
from ..session import Session
from .query_cubes import QueryCubes


@final
class _StartPrivateParameters(TypedDict):
    debug: NotRequired[bool]
    debug_id: NotRequired[str]
    session_config_path: NotRequired[Path | str]
    port_path: NotRequired[Path | str]
    api_token: NotRequired[str]  # Used by Atoti Platform


# Only add methods and properties to this class if they are specific to query sessions.
# See comment in `BaseSession` for more information.
@final
class QuerySession(AbstractContextManager["QuerySession"]):
    @classmethod
    def start(
        cls,
        config: SessionConfig | None = None,
        /,
        **kwargs: Unpack[_StartPrivateParameters],
    ) -> QuerySession:
        if config is None:
            config = SessionConfig()

        with ExitStack() as exit_stack:
            client, server_subprocess, session_id = exit_stack.enter_context(
                started_session_resources(
                    address=None,
                    config=config,
                    enable_py4j_auth=True,
                    distributed=True,
                    py4j_server_port=None,
                    debug=kwargs.get("debug", False),
                    debug_id=kwargs.get("debug_id"),
                    session_config_path=kwargs.get("session_config_path"),
                    port_path=kwargs.get("port_path"),
                    api_token=kwargs.get("api_token"),
                ),
            )
            session = Session(
                auto_join_clusters=False,
                client=client,
                server_subprocess=server_subprocess,
                session_id=session_id,
            )
            session._warn_if_license_about_to_expire()
            session._exit_stack.push(exit_stack.pop_all())
            return QuerySession(session=session)

    def __init__(self, *, session: Session):
        self._session: Final = session

    def __del__(self) -> None:
        # See comment in `Session.__del__` for more information.
        self.__exit__(None, None, None)

    @override
    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        exception_traceback: TracebackType | None,
    ) -> None:
        self._session.__exit__(exception_type, exception_value, exception_traceback)

    @property
    def query_cubes(self) -> QueryCubes:
        return QueryCubes(client=self._session._client)

    @property
    def session(self) -> Session:
        """The session to interact with this query session.

        It is equivalent to calling :meth:`atoti.Session.connect` with the *url* of this query session and an *authentication* granting full access.
        """
        return self._session
