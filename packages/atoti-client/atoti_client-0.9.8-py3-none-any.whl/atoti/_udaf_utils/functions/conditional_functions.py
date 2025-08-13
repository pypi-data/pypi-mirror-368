"""Java function implementations for conditional operations."""

from ..java_function import ExistingJavaFunction
from ._operator_package import OPERATOR_PACKAGE

EQ_FUNCTION = ExistingJavaFunction(
    method_call_string="ConditionalOperator.eq",
    import_package=OPERATOR_PACKAGE,
)


NEQ_FUNCTION = ExistingJavaFunction(
    method_call_string="ConditionalOperator.neq",
    import_package=OPERATOR_PACKAGE,
)

GT_FUNCTION = ExistingJavaFunction(
    method_call_string="ConditionalOperator.gt",
    import_package=OPERATOR_PACKAGE,
)

GTE_FUNCTION = ExistingJavaFunction(
    method_call_string="ConditionalOperator.gte",
    import_package=OPERATOR_PACKAGE,
)

LT_FUNCTION = ExistingJavaFunction(
    method_call_string="ConditionalOperator.lt",
    import_package=OPERATOR_PACKAGE,
)

LTE_FUNCTION = ExistingJavaFunction(
    method_call_string="ConditionalOperator.lte",
    import_package=OPERATOR_PACKAGE,
)
