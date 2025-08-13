from typing import final

from pydantic import FilePath
from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ClientCertificateConfig:
    """The JKS truststore config to enable client certificate authentication (also called mutual TLS or mTLS) on the application.

    See Also:
        :class:`~atoti.ClientCertificate`.
    """

    trust_store: FilePath
    """Path to the truststore file generated with the certificate used to sign client certificates."""

    trust_store_password: str | None
    """Password protecting the truststore."""

    username_regex: str = "CN=(.*?)(?:,|$)"
    """Regex to extract the username from the certificate."""
