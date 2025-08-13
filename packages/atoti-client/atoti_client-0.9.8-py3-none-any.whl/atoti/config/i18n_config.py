from typing import final

from pydantic import DirectoryPath
from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class I18nConfig:
    """The internationalization config.

    Note:
        This feature is not part of the community edition: it needs to be :doc:`unlocked </guides/unlocking_all_features>`.
    """

    default_locale: str | None = None
    """The default locale to use for internationalizing the session."""

    translations: DirectoryPath | None = None
    """The directory from which translation files will be loaded.

    This directory should contain a list of files named after their corresponding locale (e.g. ``en-US.json`` for US translations).
    The application will behave differently depending on how :func:`atoti.Session`'s *user_content_storage*  parameter is configured:

    * If *user_content_storage* is a path to a file:

      * If a value is specified for *translations*, those files will be uploaded to the local content storage, overriding any previously defined translations.
      * If no value is specified for *translations*, the default translations for Atoti will be uploaded to the local user content storage.

    * If a remote user content storage has been configured:

      * If a value is specified for *translations*, this data will be pushed to the remote user content storage, overriding any previously existing values.
      * If no value has been specified for *translations* and translations exist in the remote user content storage, those values will be loaded into the session.
      * If no value has been specified for *translations* and no translations exist in the remote user content storage, the default translations for Atoti will be uploaded to the remote user content storage.

    """
