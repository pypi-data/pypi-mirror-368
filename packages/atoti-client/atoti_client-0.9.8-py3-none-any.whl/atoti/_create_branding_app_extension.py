from pathlib import Path, PurePosixPath
from shutil import copytree
from tempfile import mkdtemp

from .app_extension import _APP_EXTENSIONS_DIRECTORY

_EXTENSION_NAME = "@atoti/branding-app-extension"

_SOURCE_EXTENSION_DIRECTORY = _APP_EXTENSIONS_DIRECTORY / PurePosixPath(_EXTENSION_NAME)

_TITLE_PLACEHOLDER = "_ATOTI_TITLE_PLACEHOLDER"


def create_branding_app_extension(*, title: str) -> dict[str, Path]:
    directory = Path(mkdtemp(prefix="atoti-branding-app-extension-"))
    copytree(_SOURCE_EXTENSION_DIRECTORY, directory, dirs_exist_ok=True)

    found_title_placeholder = False
    for file_path in directory.glob("**/*.js"):
        source = file_path.read_text(encoding="utf8")

        if _TITLE_PLACEHOLDER not in source:
            continue

        found_title_placeholder = True
        source = source.replace(_TITLE_PLACEHOLDER, title)
        file_path.write_text(source, encoding="utf8")
    assert found_title_placeholder

    return {_EXTENSION_NAME: directory}
