from typing import Literal

from ._graphql_client import RelationshipOptionality as _GraphQlRelationshipOptionality

RelationshipOptionality = Literal["mandatory", "optional"]


def relationship_optionality_to_graphql(
    relationship_optionality: RelationshipOptionality,
    /,
) -> _GraphQlRelationshipOptionality:
    match relationship_optionality:
        case "mandatory":
            return _GraphQlRelationshipOptionality.MANDATORY
        case "optional":
            return _GraphQlRelationshipOptionality.OPTIONAL
