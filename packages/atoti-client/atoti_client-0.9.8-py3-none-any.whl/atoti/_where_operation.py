from dataclasses import dataclass
from itertools import chain
from typing import final

from typing_extensions import override

from ._identification import Identifier, IdentifierT_co
from ._operation import Operand, OperandCondition, Operation


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class WhereOperation(Operation[IdentifierT_co]):
    condition: OperandCondition[IdentifierT_co]
    true_value: Operand[IdentifierT_co]
    false_value: Operand[IdentifierT_co] | None

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        operands = [
            self.condition,
            self.true_value,
            self.false_value,
        ]
        return frozenset(
            chain.from_iterable(
                self._get_identifier_types(operand) for operand in operands
            ),
        )
