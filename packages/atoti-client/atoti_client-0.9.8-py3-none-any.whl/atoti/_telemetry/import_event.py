from __future__ import annotations

import os
import platform
from dataclasses import field
from functools import cache
from typing import final
from uuid import UUID, uuid4

from _atoti_core import get_atoti_home
from pydantic.dataclasses import dataclass

from .._env import get_env_flag
from .._ipython import get_ipython
from .._pydantic import PYDANTIC_CONFIG
from .._version import VERSION
from .event import Event

_INSTALLATION_ID_PATH = get_atoti_home() / "installation_id.txt"
_ENV_VAR_NAME_TO_ENV_NAME = {
    "CIRCLECI": "CircleCI",  # https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables
    "GITHUB_ACTIONS": "Github Actions",  # https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables
    "TRAVIS": "TravisCI",  # https://docs.travis-ci.com/user/environment-variables/#default-environment-variables
    "JENKINS_URL": "Jenkins",  # https://github.com/jenkinsci/jenkins/blob/master/core/src/main/resources/jenkins/model/CoreEnvironmentContributor/buildEnv.properties
    "teamcity.agent.name": "TeamCity",  # https://www.jetbrains.com/help/teamcity/predefined-build-parameters.html#Predefined+Agent+Environment+Parameters
    "BITBUCKET_BUILD_NUMBER": "Bitbucket",  # https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
    "GITLAB_CI": "GitLab",  # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
    "KAGGLE_KERNEL_RUN_TYPE": "Kaggle",  # https://www.kaggle.com/code/jamesmcguigan/kaggle-environment-variables-os-environ/notebook
    # /!\ Also uses ZMQInteractiveShell.
}
_IPYTHON_SHELL_TO_ENV_NAME = {
    "ZMQInteractiveShell": "Jupyter",  # "https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook"
    "google.colab": "Colab",  # https://stackoverflow.com/questions/53581278/test-if-notebook-is-running-on-google-colab
}


def _get_installation_id_from_file() -> str | None:
    if not _INSTALLATION_ID_PATH.exists():
        return None

    try:
        content = _INSTALLATION_ID_PATH.read_text(encoding="utf8").strip()
        UUID(content)
    except (OSError, ValueError):
        # The file cannot be read or its content is not a valid UUID.
        return None
    else:
        return content


def _write_installation_id_to_file(installation_id: str) -> None:
    try:
        _INSTALLATION_ID_PATH.parent.mkdir(
            exist_ok=True,
            parents=True,
        )
        _INSTALLATION_ID_PATH.write_text(f"{installation_id}\n", encoding="utf8")
    except OSError:
        # To prevent bothering the user, do nothing even if the id could not be written to the file.
        ...


@cache
def _get_installation_id() -> str:
    existing_id = _get_installation_id_from_file()

    if existing_id is not None:
        return existing_id

    new_id = str(uuid4())

    _write_installation_id_to_file(new_id)

    return new_id


def _get_environment() -> str | None:
    for env_var_name, env_name in _ENV_VAR_NAME_TO_ENV_NAME.items():
        if env_var_name in os.environ:
            return env_name

    if get_env_flag("CI"):
        return "CI"

    ipython = get_ipython()

    if ipython is not None:
        return next(
            (
                env_name
                for shell_name, env_name in _IPYTHON_SHELL_TO_ENV_NAME.items()
                if shell_name in str(ipython)
            ),
            "IPython",
        )
    return None


@final
@dataclass(config=PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ImportEvent(Event):
    """Triggered when the library is imported."""

    event_type: str = field(default="import", init=False)
    installation_id: str = field(default_factory=_get_installation_id, init=False)
    operating_system: str = field(default_factory=platform.platform, init=False)
    python_version: str = field(default_factory=platform.python_version, init=False)
    version: str = field(default=VERSION, init=False)
    environment: str | None = field(default_factory=_get_environment, init=False)
