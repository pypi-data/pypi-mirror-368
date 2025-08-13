from typing import Final, final

from .._client import Client
from .default_roles import DefaultRoles


@final
class KerberosSecurity:
    """Manage Kerberos security on the session.

    Note:
        This requires :attr:`atoti.SecurityConfig.sso` to be an instance of :class:`~atoti.KerberosConfig`.

    See Also:
        :attr:`~atoti.security.Security.ldap` for a similar usage example.
    """

    def __init__(self, *, client: Client) -> None:
        self._client: Final = client

    @property
    def default_roles(self) -> DefaultRoles:
        return DefaultRoles(authentication_type="KERBEROS", client=self._client)
