from __future__ import annotations

from collections.abc import MutableMapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import deprecated

from .._client import Client
from .._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from .._identification import Role, UserName
from .._tables_restriction_condition import TablesRestrictionCondition
from .._tables_restrictions import Restrictions
from ._individual_roles import IndividualRoles
from .basic_authentication_security import BasicAuthenticationSecurity
from .kerberos_security import KerberosSecurity
from .ldap_security import LdapSecurity
from .oidc_security import OidcSecurity


@final
class Security:
    """Manage the parts of the security config that can be changed without restarting the :class:`~atoti.Session`.

    Note:
        This feature is not part of the community edition: it needs to be :doc:`unlocked </guides/unlocking_all_features>`.

    * Users with the :guilabel:`ROLE_ADMIN` are administrators: they have full access to the application.
    * Non-administrator users without the :guilabel:`ROLE_USER` will not be able to access the application.
      See :attr:`individual_roles` for an example.

    """

    def __init__(
        self,
        *,
        basic_credentials: MutableMapping[UserName, str],
        client: Client,
    ):
        self._basic_credentials: Final = basic_credentials
        self._client: Final = client

    @property
    @deprecated(
        "`Session.security.restrictions is deprecated, use `Session.tables.restrictions` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def restrictions(self) -> MutableMapping[Role, TablesRestrictionCondition]:
        """Tables restrictions.

        :meta private:
        """
        return Restrictions(client=self._client)

    @property
    def individual_roles(self) -> MutableMapping[UserName, AbstractSet[Role]]:
        """Mapping from username to roles granted on top of the ones that can be added by authentication providers.

        Example:
            >>> session_config = tt.SessionConfig(security=tt.SecurityConfig())
            >>> session = tt.Session.start(session_config)
            >>> username = "John"
            >>> username in session.security.individual_roles
            False
            >>> session.security.individual_roles[username] = {
            ...     "ROLE_USA",
            ...     "ROLE_USER",
            ... }
            >>> sorted(session.security.individual_roles[username])
            ['ROLE_USA', 'ROLE_USER']
            >>> session.security.individual_roles[username] -= {"ROLE_USA"}
            >>> session.security.individual_roles[username]
            frozenset({'ROLE_USER'})
            >>> # Removing all the roles will prevent the user from accessing the application:
            >>> del session.security.individual_roles[username]
            >>> username in session.security.individual_roles
            False

            .. doctest::
                :hide:

                >>> del session

        """
        return IndividualRoles(client=self._client)

    @property
    @deprecated(
        "`security.basic` is deprecated, use `security.basic_authentication` instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def basic(self) -> BasicAuthenticationSecurity:
        """The basic authentication security.

        :meta private:
        """
        return self.basic_authentication

    @property
    def basic_authentication(self) -> BasicAuthenticationSecurity:
        return BasicAuthenticationSecurity(credentials=self._basic_credentials)

    @property
    def kerberos(self) -> KerberosSecurity:
        return KerberosSecurity(client=self._client)

    @property
    def ldap(self) -> LdapSecurity:
        return LdapSecurity(client=self._client)

    @property
    def oidc(self) -> OidcSecurity:
        return OidcSecurity(client=self._client)
