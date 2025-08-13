from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from pathlib import Path

from .._client import Client
from .._client._has_compatible_standard_runtime_api import (
    has_compatible_standard_runtime_api,
)
from .._py4j_client import Py4jClient
from .._session_id import SessionId
from .._transaction import get_data_model_transaction_id
from ..authentication import Authenticate, ClientCertificate
from ._py4j_configuration import get_py4j_configuration


@contextmanager
def connected_session_client(
    url: str,
    /,
    *,
    authentication: Authenticate | ClientCertificate | None,
    certificate_authority: Path | None,
    session_id: SessionId,
) -> Generator[Client, None, None]:
    with ExitStack() as exit_stack:
        client = exit_stack.enter_context(
            Client._create(
                url,
                authentication=authentication,
                certificate_authority=certificate_authority,
                get_data_model_transaction_id=lambda: get_data_model_transaction_id(
                    session_id
                ),
                py4j_client=None,
            ),
        )

        if has_compatible_standard_runtime_api(client._server_versions):
            py4j_configuration = get_py4j_configuration(client=client)
            if py4j_configuration is not None:
                # Remove this once the Py4J -> GraphQL migration is complete.
                client._py4j_client = exit_stack.enter_context(  # type: ignore[misc] # pyright: ignore[reportAttributeAccessIssue]
                    Py4jClient.create(
                        address=client._http_client.base_url.host,
                        detached=True,
                        distributed=py4j_configuration.distributed,
                        py4j_java_port=py4j_configuration.port,
                        py4j_auth_token=py4j_configuration.token,
                        session_id=session_id,
                    ),
                )

        yield client
