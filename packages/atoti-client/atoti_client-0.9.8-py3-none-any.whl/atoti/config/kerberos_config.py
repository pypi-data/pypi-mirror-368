from typing import final

from pydantic import FilePath
from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._case_insensitive_security_provider_config import (
    CaseInsensitiveSecurityProviderConfig,
)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class KerberosConfig(CaseInsensitiveSecurityProviderConfig):
    """The config to delegate authentication to `Kerberos <https://web.mit.edu/kerberos/>`__.

    The user's roles can be defined using :attr:`atoti.security.Security.kerberos` and :attr:`~atoti.security.Security.individual_roles`.
    """

    service_principal: str
    """The principal that the session will use."""

    keytab: FilePath | None = None
    """The path to the keytab file to use."""

    krb5_config: FilePath | None = None
    """The path to the Kerberos config file.

    Defaults to the OS-specific default location.
    """
