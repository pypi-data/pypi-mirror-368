from dataclasses import dataclass
from itertools import chain
from typing import final

from typing_extensions import override

from ._identification import Identifier, IdentifierT_co
from ._operation import Operand, Operation


@final
@dataclass(eq=False, frozen=True, kw_only=True)
class FunctionOperation(Operation[IdentifierT_co]):
    function_key: str
    operands: tuple[Operand[IdentifierT_co] | None, ...] = ()

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(
            chain.from_iterable(
                self._get_identifier_types(operand) for operand in self.operands
            ),
        )
