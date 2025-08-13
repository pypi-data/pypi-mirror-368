from dataclasses import KW_ONLY
from pathlib import Path
from typing import final

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ClientCertificate:
    """A client certificate to :meth:`~atoti.Session.connect` to a session configured with :class:`~atoti.ClientCertificateConfig`.

    Example:
        .. doctest::
            :hide:

            >>> certificates_directory = TEST_RESOURCES_PATH / "config" / "certificates"

        >>> certificate_authority = certificates_directory / "root-CA.crt"
        >>> session_config = tt.SessionConfig(
        ...     security=tt.SecurityConfig(
        ...         client_certificate=tt.ClientCertificateConfig(
        ...             trust_store=certificates_directory / "truststore.jks",
        ...             trust_store_password="changeit",
        ...         ),
        ...         https=tt.HttpsConfig(
        ...             certificate=certificates_directory / "localhost.p12",
        ...             certificate_authority=certificate_authority,
        ...             password="changeit",
        ...         ),
        ...     )
        ... )
        >>> session = tt.Session.start(session_config)
        >>> session.security.individual_roles["atoti"] = {"ROLE_USER"}
        >>> # The session requires authentication:
        >>> tt.Session.connect(
        ...     session.url, certificate_authority=certificate_authority
        ... )  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        httpx.HTTPStatusError: Client error '401 '...
        >>> connected_session = tt.Session.connect(
        ...     session.url,
        ...     authentication=tt.ClientCertificate(
        ...         certificates_directory / "client.pem",
        ...         keyfile=certificates_directory / "client.key",
        ...     ),
        ...     certificate_authority=certificate_authority,
        ... )

        .. doctest::
            :hide:

            >>> del connected_session
            >>> del session
    """

    certificate: Path
    """Path to the ``.pem`` file containing the client certificate."""

    _: KW_ONLY

    keyfile: Path | None = None
    """Path to the certificate ``.key`` file."""

    password: str | None = None
    """The certificate password."""
