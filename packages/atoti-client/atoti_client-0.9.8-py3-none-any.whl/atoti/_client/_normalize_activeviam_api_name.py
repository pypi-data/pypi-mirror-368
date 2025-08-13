from ._server_versions import ServerVersions


# Remove when dropping support for Atoti Server < 6.0.0-M1.
def normalize_activeviam_api_name(
    api_name: str, /, *, server_versions: ServerVersions
) -> str:
    legacy_api_name = api_name.removeprefix("activeviam/")
    return (
        api_name
        if legacy_api_name == api_name or api_name in server_versions.apis
        else legacy_api_name
    )
