import os
import re
from pathlib import Path
from textwrap import dedent
from typing import Literal

from _atoti_core import LICENSE_KEY_ENV_VAR_NAME, get_atoti_home

from ._env import get_env_flag
from ._version import VERSION

EULA = (Path(__file__).parent / "LICENSE").read_text(encoding="utf8")

COPIED_EULA_PATH = get_atoti_home() / "LICENSE"
HIDE_EULA_MESSAGE_ENV_VAR_NAME = "ATOTI_HIDE_EULA_MESSAGE"


EULA_MESSAGE = dedent(
    f"""\
    Welcome to Atoti {VERSION}!

    By using this community edition, you agree with the license available at https://docs.activeviam.com/products/atoti/python-sdk/latest/eula.html.
    Browse the official documentation at https://docs.activeviam.com/products/atoti/python-sdk.
    Join the community at https://www.atoti.io/register.

    Atoti collects telemetry data, which is used to help understand how to improve the product.
    If you don't wish to send usage data, you can request a trial license at https://www.atoti.io/evaluation-license-request.

    You can hide this message by setting the `{HIDE_EULA_MESSAGE_ENV_VAR_NAME}` environment variable to True.""",
)


def hide_new_eula_message() -> None:
    """Copy the current end-user license agreement to Atoti's home directory."""
    COPIED_EULA_PATH.parent.mkdir(parents=True, exist_ok=True)
    COPIED_EULA_PATH.write_text(EULA, encoding="utf8")


EULA_CHANGED_MESSAGE = dedent(
    f"""\
    Thanks for updating to Atoti {VERSION}!

    The license agreement has changed, it's available at https://docs.activeviam.com/products/atoti/python-sdk/latest/eula.html.

    You can hide this message by calling `atoti.{hide_new_eula_message.__name__}()`.""",
)


def _get_eula_change() -> Literal["version-only", "other"] | None:
    copied_eula = COPIED_EULA_PATH.read_text(encoding="utf8")

    if copied_eula == EULA:
        return None

    previous, new = (
        re.sub(r"\d+\.\d+\.\d+[^\s]+", "ATOTI_VERSION_PLACEHOLDER", text).lower()
        for text in (copied_eula, EULA)
    )
    return "version-only" if previous == new else "other"


def print_eula_message() -> None:
    if LICENSE_KEY_ENV_VAR_NAME in os.environ:
        # The validity of the license key will be checked by each started Java process.
        return

    if get_env_flag(HIDE_EULA_MESSAGE_ENV_VAR_NAME):
        if COPIED_EULA_PATH.exists():
            eula_change = _get_eula_change()
            if eula_change == "other":
                print(EULA_CHANGED_MESSAGE)  # noqa: T201
            elif eula_change == "version-only":
                hide_new_eula_message()
        else:
            COPIED_EULA_PATH.parent.mkdir(parents=True, exist_ok=True)
            hide_new_eula_message()
    else:
        print(EULA_MESSAGE)  # noqa: T201
