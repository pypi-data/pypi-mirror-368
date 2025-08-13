"""Java function implementation for array functions."""

from ...type import DOUBLE, DOUBLE_ARRAY
from ..java_function import CustomJavaFunction

ARRAY_SUM = CustomJavaFunction(
    [("vector", DOUBLE_ARRAY)],
    method_name="array_sum",
    method_body="return vector.sumDouble();\n",
    output_type=DOUBLE,
)


ARRAY_MEAN = CustomJavaFunction(
    [("vector", DOUBLE_ARRAY)],
    method_name="array_mean",
    method_body="return vector.average();",
    output_type=DOUBLE,
)
