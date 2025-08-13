from typing import Final, final

from .._client import Client
from .default_roles import DefaultRoles
from .role_mapping import RoleMapping


@final
class LdapSecurity:
    """Manage LDAP security on the session.

    Note:
        This requires :attr:`atoti.SecurityConfig.sso` to be an instance of :class:`~atoti.LdapConfig`.

    Example:
        >>> session_config = tt.SessionConfig(
        ...     security=tt.SecurityConfig(
        ...         sso=tt.LdapConfig(
        ...             url="ldap://example.com:389",
        ...             base_dn="dc=example,dc=com",
        ...             user_search_base="ou=people",
        ...             group_search_base="ou=roles",
        ...             username_case_conversion="lower",
        ...         )
        ...     )
        ... )
        >>> session = tt.Session.start(session_config)
        >>> table = session.create_table(
        ...     "Restrictions example",
        ...     data_types={"City": "String"},
        ... )
        >>> session.tables.restrictions["ROLE_MATHS"] = table["City"] == "Paris"

        Roles from the authentication provider can be mapped to roles in the session:

        >>> session.security.ldap.role_mapping["MATHEMATICIANS"] = {
        ...     "ROLE_MATHS",
        ...     "ROLE_USER",
        ... }
        >>> sorted(session.security.ldap.role_mapping["MATHEMATICIANS"])
        ['ROLE_MATHS', 'ROLE_USER']

        Default roles can be given to users who have no individual or mapped roles granted:

        >>> session.security.ldap.default_roles.add("ROLE_USER")
        >>> session.security.ldap.default_roles
        {'ROLE_USER'}

        .. doctest::
            :hide:

            >>> del session

    """

    def __init__(self, *, client: Client) -> None:
        self._client: Final = client

    @property
    def default_roles(self) -> DefaultRoles:
        return DefaultRoles(authentication_type="LDAP", client=self._client)

    @property
    def role_mapping(self) -> RoleMapping:
        """The role mapping is done with the roles included in the ID Token sent by the authentication provider."""
        return RoleMapping(authentication_type="LDAP", client=self._client)
