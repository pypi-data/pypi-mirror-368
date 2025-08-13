from functools import cache

from ._resources_directory import RESOURCES_DIRECTORY

_ATOTI_SERVER_VERSION_PATH = RESOURCES_DIRECTORY / "atoti-server-version.txt"


@cache
def atoti_server_version() -> str:
    """Return the version of Atoti Server this client was built for."""
    return _ATOTI_SERVER_VERSION_PATH.read_text().strip()
