"""Java function implementations for arithmetic operations."""

from ..java_function import ExistingJavaFunction
from ._operator_package import OPERATOR_PACKAGE

ADD_FUNCTION = ExistingJavaFunction(
    method_call_string="ArithmeticOperator.add",
    import_package=OPERATOR_PACKAGE,
)

SUB_FUNCTION = ExistingJavaFunction(
    method_call_string="ArithmeticOperator.minus",
    import_package=OPERATOR_PACKAGE,
)

TRUEDIV_FUNCTION = ExistingJavaFunction(
    method_call_string="ArithmeticOperator.divide",
    import_package=OPERATOR_PACKAGE,
)

MUL_FUNCTION = ExistingJavaFunction(
    method_call_string="ArithmeticOperator.multiply",
    import_package=OPERATOR_PACKAGE,
)
