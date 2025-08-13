from __future__ import annotations

from dataclasses import replace
from pathlib import Path

# Remove this once the session config serialization logic on the Java side is synchronized with the Python side.
from pydantic_core import to_json  # pylint: disable=undeclared-dependency

from atoti._pydantic import get_type_adapter

from .._create_branding_app_extension import create_branding_app_extension
from .._jdbc import H2_DRIVER, get_h2_url, normalize_jdbc_url
from ..config import (
    KerberosConfig,
    LdapConfig,
    OidcConfig,
    SecurityConfig,
    SessionConfig,
)


def apply_plugin_config_hooks(config: SessionConfig) -> SessionConfig:
    for plugin_key, plugin in config.plugins.items():
        config = plugin.session_config_hook(config)
        assert isinstance(
            config,
            SessionConfig,
        ), f"Plugin `{plugin_key}` returned an invalid session config: `{config}`."
    return config


def add_branding_app_extension_to_config(config: SessionConfig, /) -> SessionConfig:
    if config.branding is None:
        return config

    branding_app_extension = create_branding_app_extension(title=config.branding.title)

    return replace(
        config,
        app_extensions={
            **config.app_extensions,
            **branding_app_extension,
        },
    )


def convert_session_config_to_json(
    config: SessionConfig, *, api_token: str, distributed: bool
) -> str:
    config_data: dict[str, object] = {}

    if config.app_extensions:
        config_data["app_extensions"] = get_type_adapter(
            dict[str, Path],
        ).dump_python({**config.app_extensions})

    _dump_into_config(
        config_data, config.auto_distribution, key="auto_distribution_config"
    )
    _dump_into_config(config_data, config.branding, key="branding")
    _dump_into_config(config_data, config.i18n, key="i18n")
    _dump_into_config(config_data, config.logging, key="logging")

    if isinstance(config.license_key, str):
        # Allows debugging the Java side of an Atoti Python SDK test with the same license key as the one set up on the Python side.
        config_data["license"] = config.license_key

    config_data["ready"] = config.ready
    if config.security:
        config_data.update(_convert_security_config_to_dict(config.security))

    if isinstance(config.user_content_storage, Path):
        config_data["user_content_storage"] = {
            "url": normalize_jdbc_url(get_h2_url(config.user_content_storage)),
            "driver": H2_DRIVER,
            "hibernate_options": {},
        }
    else:
        _dump_into_config(
            config_data,
            config.user_content_storage,
            key="user_content_storage",
        )

    config_data["features"] = [
        plugin._key for plugin in config.plugins.values() if plugin._key
    ]
    config_data["api_token"] = api_token
    config_data["distributed"] = distributed

    return to_json(config_data).decode()


def _dump_into_config(
    config_data: dict[str, object],
    value: object | None,
    *,
    key: str,
) -> None:
    if value:
        config_data[key] = get_type_adapter(type(value)).dump_python(value)


def _convert_security_config_to_dict(config: SecurityConfig, /) -> dict[str, object]:  # noqa: C901
    config_data: dict[str, object] = {}
    if config.client_certificate:
        config_data["client_certificate"] = get_type_adapter(
            type(config.client_certificate),
        ).dump_python(config.client_certificate)

    if config.https:
        config_data["https"] = get_type_adapter(
            type(config.https),
        ).dump_python(config.https)

    if config.jwt and config.jwt.key_pair:
        config_data["jwt"] = get_type_adapter(
            type(config.jwt),
        ).dump_python(config.jwt)

    if config.same_site != SecurityConfig().same_site:
        config_data["same_site"] = get_type_adapter(
            type(config.same_site),
        ).dump_python(config.same_site)

    if config.cors:
        config_data["cors"] = get_type_adapter(
            type(config.cors),
        ).dump_python(config.cors)

    authentication: dict[str, object] = {}

    match config.sso:
        case KerberosConfig():
            authentication["kerberos"] = get_type_adapter(
                type(config.sso),
            ).dump_python(config.sso)
        case LdapConfig():
            authentication["ldap"] = get_type_adapter(
                type(config.sso),
            ).dump_python(config.sso)
        case OidcConfig():
            oidc_config = get_type_adapter(
                type(config.sso),
            ).dump_python(config.sso)

            # See https://github.com/activeviam/activepivot/blob/5ea766c9af9fbce31919112ef493072749569fcd/atoti/patachou/server/server-starter/src/main/java/io/atoti/server/starter/api/configuration/authentication/OidcAuthenticationConfig.java#L42
            oidc_config["access_token_aud"] = oidc_config[
                "access_token_allowed_audience"
            ]
            del oidc_config["access_token_allowed_audience"]

            # See https://github.com/activeviam/activepivot/blob/5ea766c9af9fbce31919112ef493072749569fcd/atoti/patachou/server/server-starter/src/main/java/io/atoti/server/starter/api/configuration/authentication/OidcAuthenticationConfig.java#L45.
            if oidc_config["access_token_issuer_claim"] != "issuer":  # noqa: S105
                oidc_config["access_token_issuer_url_config_metadata_key"] = (
                    oidc_config["access_token_issuer_claim"]
                )
            del oidc_config["access_token_issuer_claim"]

            authentication["oidc"] = oidc_config
        case None:
            # Ideally, the basic authentication config would be taken into account even when sso is configured.
            authentication["basic"] = get_type_adapter(
                type(config.basic_authentication),
            ).dump_python(
                config.basic_authentication,
            )
    config_data["authentication"] = authentication
    return config_data
