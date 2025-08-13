from typing import Final, final

from .._client import Client
from .default_roles import DefaultRoles
from .role_mapping import RoleMapping


@final
class OidcSecurity:
    """Manage OIDC security on the session.

    Note:
        This requires :attr:`atoti.SecurityConfig.sso` to be an instance of :class:`~atoti.OidcConfig`.

    Example:
        >>> import os
        >>> session_config = tt.SessionConfig(
        ...     port=1234,
        ...     security=tt.SecurityConfig(
        ...         sso=tt.OidcConfig(
        ...             provider_id="auth0",
        ...             issuer_url=os.environ["AUTH0_ISSUER"],
        ...             client_id=os.environ["AUTH0_CLIENT_ID"],
        ...             client_secret=os.environ["AUTH0_CLIENT_SECRET"],
        ...             name_claim="email",
        ...             scopes={"openid", "email", "profile", "username"},
        ...             roles_claims={"https://activeviam.com/roles"},
        ...         ),
        ...     ),
        ... )
        >>> session = tt.Session.start(session_config)
        >>> table = session.create_table(
        ...     "Restrictions example",
        ...     data_types={"Country": "String"},
        ... )
        >>> session.tables.restrictions.update(
        ...     {
        ...         "ROLE_FRANCE": table["Country"] == "France",
        ...         "ROLE_UK": table["Country"] == "UK",
        ...     }
        ... )

        Roles from the authentication provider's ID Token can be mapped to roles in the session:

        >>> session.security.oidc.role_mapping.update(
        ...     {"atoti user": {"ROLE_USER"}, "France": {"ROLE_FRANCE"}}
        ... )
        >>> session.security.oidc.role_mapping
        {'atoti user': frozenset({'ROLE_USER'}), 'France': frozenset({'ROLE_FRANCE'})}

        Default roles can be given to users who have been granted no individual and mapped roles:

        >>> session.security.oidc.default_roles.add("ROLE_UK")
        >>> session.security.oidc.default_roles
        {'ROLE_UK'}

        Note that the name claim is required in the access token to identify the user for any client application.

        .. doctest::
            :hide:

            >>> del session

    """

    def __init__(self, *, client: Client) -> None:
        self._client: Final = client

    @property
    def default_roles(self) -> DefaultRoles:
        return DefaultRoles(authentication_type="OIDC", client=self._client)

    @property
    def role_mapping(self) -> RoleMapping:
        """The role mapping is done with the roles included in the ID Token sent by the authentication provider."""
        return RoleMapping(authentication_type="OIDC", client=self._client)
