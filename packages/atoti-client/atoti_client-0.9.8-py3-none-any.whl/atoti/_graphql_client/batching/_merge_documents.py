from collections.abc import Sequence

from graphql import (
    ArgumentNode,
    DocumentNode,
    FieldNode,
    FragmentDefinitionNode,
    NameNode,
    OperationDefinitionNode,
    OperationType,
    SelectionNode,
    SelectionSetNode,
    VariableDefinitionNode,
    VariableNode,
    print_ast,
)

from ._naming import get_merged_name


def _get_merged_selection(
    selection: SelectionNode, /, *, unique_id: int
) -> SelectionNode:
    match selection:
        case FieldNode():
            return FieldNode(
                alias=NameNode(
                    value=get_merged_name(
                        selection.name.value
                        if selection.alias is None
                        else selection.alias.value,
                        index=unique_id,
                    )
                ),
                arguments=[
                    ArgumentNode(
                        name=argument.name,
                        value=VariableNode(
                            name=NameNode(
                                value=get_merged_name(
                                    argument.value.name.value,
                                    index=unique_id,
                                )
                            )
                        )
                        if isinstance(argument.value, VariableNode)
                        else argument.value,
                    )
                    for argument in selection.arguments or []
                ],
                directives=selection.directives,
                name=selection.name,
                selection_set=selection.selection_set,
            )
        case _:
            raise TypeError(f"Unexpected selection: {selection}")


def _get_merged_variable_definition(
    variable_definition: VariableDefinitionNode, /, *, unique_id: int
) -> VariableDefinitionNode:
    return VariableDefinitionNode(
        default_value=variable_definition.default_value,
        directives=variable_definition.directives,
        variable=variable_definition.variable.__class__(
            name=NameNode(
                value=get_merged_name(
                    variable_definition.variable.name.value,
                    index=unique_id,
                )
            )
        ),
        type=variable_definition.type,
    )


def merge_documents(
    documents: Sequence[DocumentNode], /, *, operation_name: str = "MergedOperation"
) -> DocumentNode:
    """Merge multiple documents into a single one.

    Args:
        documents: Each document can define several fragments but only a single operation.
            Fragments with the same name in different documents must be identical.
            All documents must define an operation of the same type.
        operation_name: The named to give to the merged operation.

    Returns:
        A document defining a single operation and possibly several fragments.
    """
    assert documents, "No documents to merge."

    if len(documents) == 1:
        return documents[0]

    operation_definition_index: int = 0
    operation_type: OperationType = next(
        definition.operation
        for definition in documents[0].definitions
        if isinstance(definition, OperationDefinitionNode)
    )

    fragments_definitions: dict[str, FragmentDefinitionNode] = {}
    selections: list[SelectionNode] = []
    variable_definitions: list[VariableDefinitionNode] = []

    for document in documents:
        operation_definition_count: int = 0

        for definition in document.definitions:
            match definition:
                case FragmentDefinitionNode():
                    fragment_name = definition.name.value
                    existing_fragment_definition = fragments_definitions.get(
                        fragment_name
                    )
                    if existing_fragment_definition is None:
                        fragments_definitions[fragment_name] = definition
                    else:
                        assert print_ast(existing_fragment_definition) == print_ast(
                            definition
                        ), (
                            f"Expected all `{fragment_name}` fragment definitions to be identical."
                        )
                case OperationDefinitionNode():
                    assert operation_definition_count == 0, (
                        "Expected all documents to define a single operation since otherwise it is unclear which operation should be merged."
                    )
                    operation_definition_count += 1

                    assert definition.operation == operation_type, (
                        "All operation definitions must share the same type."
                    )

                    selections.extend(
                        _get_merged_selection(
                            selection, unique_id=operation_definition_index
                        )
                        for selection in definition.selection_set.selections
                    )

                    variable_definitions.extend(
                        _get_merged_variable_definition(
                            variable_definition, unique_id=operation_definition_index
                        )
                        for variable_definition in definition.variable_definitions or []
                    )

                    operation_definition_index += 1
                case _:
                    raise TypeError(f"Unexpected document definition: {definition}")

    return DocumentNode(
        definitions=[
            *fragments_definitions.values(),
            OperationDefinitionNode(
                directives=[],
                name=NameNode(value=operation_name),
                operation=operation_type,
                selection_set=SelectionSetNode(selections=selections),
                variable_definitions=variable_definitions,
            ),
        ]
    )
