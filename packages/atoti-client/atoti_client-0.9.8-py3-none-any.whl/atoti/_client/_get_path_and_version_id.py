from collections.abc import Sequence, Set as AbstractSet
from typing import Literal, TypeAlias, TypeVar, cast, overload

from ._normalize_activeviam_api_name import normalize_activeviam_api_name
from ._server_versions import ServerApiVersion, ServerVersions

PathType: TypeAlias = Literal["rest", "ws"]


def _get_path(
    server_api_version: ServerApiVersion, path_type: PathType, /
) -> str | None:
    match path_type:
        case "rest":
            return server_api_version.rest_path
        case "ws":
            return server_api_version.ws_path


VersionIdT_co = TypeVar("VersionIdT_co", bound=str, covariant=True)


@overload
def get_path_and_version_id(
    api_name: str,
    /,
    *,
    denied_version_ids: AbstractSet[str] = ...,
    path_type: PathType = ...,
    server_versions: ServerVersions,
) -> tuple[str, str]: ...


@overload
def get_path_and_version_id(
    api_name: str,
    /,
    *,
    allowed_version_ids: Sequence[VersionIdT_co],
    denied_version_ids: AbstractSet[str] = ...,
    path_type: PathType = ...,
    server_versions: ServerVersions,
) -> tuple[str, VersionIdT_co]: ...


@overload
def get_path_and_version_id(
    api_name: str,
    /,
    *,
    allowed_version_ids: Sequence[str] | None = ...,
    denied_version_ids: AbstractSet[str] = ...,
    path_type: PathType = ...,
    server_versions: ServerVersions,
) -> tuple[str, str]: ...


def get_path_and_version_id(
    api_name: str,
    /,
    *,
    allowed_version_ids: Sequence[VersionIdT_co] | None = None,
    denied_version_ids: AbstractSet[str] = frozenset(),
    path_type: PathType = "rest",
    server_versions: ServerVersions,
) -> tuple[str, VersionIdT_co]:
    api_name = normalize_activeviam_api_name(api_name, server_versions=server_versions)

    server_api = server_versions.apis.get(api_name)

    if server_api is None:
        raise RuntimeError(
            f"No API named `{api_name}` in {list(server_versions.apis)}."
        )

    path_from_version_id = {
        _version_id: _path
        for server_api_version in server_api.versions
        if (_path := _get_path(server_api_version, path_type)) is not None
        and (_version_id := server_api_version.id) not in denied_version_ids
    }

    if not path_from_version_id:
        raise RuntimeError(f"No `{api_name}` API with `{path_type}` path found.")

    path: str | None = None
    version_id: VersionIdT_co | None = None

    if allowed_version_ids is None:
        _version_id, path = max(path_from_version_id.items(), key=lambda x: int(x[0]))
        version_id = cast(VersionIdT_co, _version_id)
    else:
        assert allowed_version_ids, "Expected at least one allowed version ID."

        max_id = None
        for _version_id in allowed_version_ids:
            path = path_from_version_id.get(_version_id)
            if path is not None:
                max_id = _version_id

        version_id = max_id
        if path is None or version_id is None:
            raise RuntimeError(
                f"None of the allowed version IDs {allowed_version_ids} match the provided ones: {list(path_from_version_id)}."
            )

    return path.lstrip("/"), version_id
