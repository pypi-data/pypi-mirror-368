from collections.abc import Set as AbstractSet
from typing import Annotated, Literal, final

from pydantic import AfterValidator
from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


def _normalize_role_claim(
    role_claim: str | tuple[str, ...],
    /,
) -> tuple[str, ...]:
    return (role_claim,) if isinstance(role_claim, str) else role_claim


def _validate_scopes(scopes: AbstractSet[str]) -> frozenset[str]:
    if "openid" not in scopes:
        raise ValueError("The `openid` scope is required.")
    return frozenset(scopes)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class OidcConfig:
    """The config to delegate authentication to an `OpenID Connect <https://openid.net/connect/>`__ provider (Auth0, Google, Keycloak, etc.).

    The user's roles are defined using :attr:`atoti.security.Security.oidc` and :attr:`~atoti.security.Security.individual_roles`.

    Example:
        >>> config = tt.OidcConfig(
        ...     provider_id="auth0",
        ...     issuer_url="https://example.auth0.com",
        ...     client_id="some client ID",
        ...     client_secret="some client secret",
        ...     name_claim="email",
        ...     scopes={"openid", "email", "profile"},
        ...     roles_claims={
        ...         "https://example.com/roles",
        ...         ("other", "path", "to", "roles"),
        ...     },
        ... )

    """

    provider_id: str
    """The name of the provider.

    It is used to build the redirect URL: ``f"{session_url}/login/oauth2/code/{provider_id}"``.
    """

    issuer_url: str

    client_id: str

    client_secret: str

    use_client_secret_as_certificate: bool = False
    """If ``True``, the passed :attr:`client_secret` must be a client certificate.

    This client certificate will be passed in the ``X-Cert`` header of the HTTP request made to the OIDC provider to retrieve an access token.
    """

    name_claim: str = "sub"
    """The name of the claim in the ID token (or userinfo) to use as the name of the user."""

    roles_claims: AbstractSet[
        Annotated[
            str | tuple[str, ...],
            AfterValidator(_normalize_role_claim),
        ]
    ] = frozenset()
    """The claims of the ID token from which to extract roles to use as keys in the :attr:`~atoti.security.oidc_security.OidcSecurity.role_mapping`.

    When an element of the set is a tuple, the tuple elements will be interpreted as the parts of a path leading to a nested value in the token.
    """

    scopes: Annotated[AbstractSet[str], AfterValidator(_validate_scopes)] = frozenset()
    """The scopes to request from the authentication provider.

    The ``"openid"`` scope is required as per the OIDC specification. """

    # Do not make this public before adding a test for it.
    access_token_allowed_audience: str | None = None
    """If not ``None``, authentication will be denied if the access token audience (i.e. its ``aud`` claim) is different than this value.

    :meta private:
    """

    access_token_format: Literal["jwt", "opaque"] = "jwt"  # noqa: S105
    """The format of the access tokens delivered by the OIDC provider.

    Opaque tokens involve another request to the OIDC provider's user info endpoint to retrieve the user details.
    The URL of this user info endpoint will be fetched from the ``f"{issuer_url}/.well-known/openid-configuration"`` endpoint.

    See Also:
        Opaque tokens can be used with :class:`atoti.OAuth2ResourceOwnerPasswordAuthentication`.
    """

    # Do not make this public before adding a test for it.
    access_token_issuer_claim: str = "issuer"  # noqa: S105
    """The name of the claim in the access token that should be considered as the issuer.

    This can be set to ``"access_token_issuer"`` when using Active Directory Federation Services for instance.

    :meta private:
    """
