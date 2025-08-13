import re
from collections.abc import Set as AbstractSet
from typing import Final, Literal, TypeAlias, final

Stability: TypeAlias = Literal["experimental", "stable"]
DEFAULT_STABILITY: Stability = "experimental"


@final
class Features:
    def __init__(self, *, key_pattern: str | None) -> None:
        self._key_pattern: Final = key_pattern
        self._stability_from_key: Final[dict[str, Stability]] = {}

    def register(
        self, key: str, /, *, stability: Stability = DEFAULT_STABILITY
    ) -> None:
        assert (
            self._key_pattern is None or re.match(self._key_pattern, key) is not None
        ), (
            f"Experimental feature key `{key}` does not match the expected pattern `{self._key_pattern}`."
        )
        existing_stability = self._stability_from_key.get(key)
        assert existing_stability is None or existing_stability == stability, (
            f"Experimental feature with key `{key}` is already registered with a different stability: `{existing_stability}`."
        )
        self._stability_from_key[key] = stability

    def unregister(self, key: str, /) -> None:
        del self._stability_from_key[key]

    @property
    def unstable_feature_keys(self) -> AbstractSet[str]:
        return {
            key
            for key, stability in self._stability_from_key.items()
            if stability != "stable"
        }

    def stability(self, key: str, /) -> Stability:
        try:
            return self._stability_from_key[key]
        except KeyError:
            raise ValueError(
                f"""No experimental feature with key `{key}`, existing keys are {sorted(self._stability_from_key)}."""
            ) from None


FEATURES = Features(key_pattern=r"^[0-9a-zA-Z._]+$")
