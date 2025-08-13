from collections.abc import Collection

from pydantic import AliasChoices, AliasGenerator
from pydantic.alias_generators import to_camel


def create_camel_case_alias_generator(
    *,
    force_aliased_attribute_names: Collection[str] = (),
) -> AliasGenerator:
    def validation_alias(name: str) -> str | AliasChoices:
        camel_case_name = to_camel(name)
        return (
            camel_case_name
            if camel_case_name == name or name in force_aliased_attribute_names
            else AliasChoices(name, camel_case_name)
        )

    return AliasGenerator(
        validation_alias=validation_alias,
        serialization_alias=to_camel,
    )
