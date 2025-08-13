from .custom_order import CustomOrder
from .natural_order import NaturalOrder

Order = CustomOrder | NaturalOrder
