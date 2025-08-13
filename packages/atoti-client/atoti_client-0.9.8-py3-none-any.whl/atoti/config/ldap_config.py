from typing import final

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._case_insensitive_security_provider_config import (
    CaseInsensitiveSecurityProviderConfig,
)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class LdapConfig(CaseInsensitiveSecurityProviderConfig):
    """The config to delegate authentication to an `LDAP <https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol>`__ provider.

    The user's roles can be defined using :attr:`atoti.security.Security.ldap` and :attr:`~atoti.security.Security.individual_roles`.

    Example:
        >>> config = tt.LdapConfig(
        ...     url="ldap://example.com:389",
        ...     base_dn="dc=example,dc=com",
        ...     user_search_base="ou=people",
        ...     group_search_base="ou=roles",
        ...     username_case_conversion="lower",
        ... )
    """

    url: str
    """The LDAP URL including the protocol and port."""

    base_dn: str
    """The base Distinguished Name of the directory service."""

    manager_dn: str | None = None
    """The Distinguished Name (DN) used to log into the Directory Service and to search for user accounts.

    If ``None``, the connection to the service will be done anonymously."""

    manager_password: str | None = None
    """The password for the manager account specified in the *manager_dn* attribute."""

    user_search_filter: str = "(uid={0})"
    """The filter to search for users.

    The substituted parameter is the user's login name.
    """

    user_search_base: str = ""
    """Search base for user searches."""

    group_search_filter: str = "(uniqueMember={0})"
    """The filter to search for groups.

    The substituted parameter is the DN of the user.
    """

    group_search_base: str | None = None
    """The search base for group membership searches."""

    group_role_attribute_name: str = "cn"
    """The attribute name that maps a group to a role."""
