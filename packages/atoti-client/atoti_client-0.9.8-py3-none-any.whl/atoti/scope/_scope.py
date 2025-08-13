from .cumulative_scope import CumulativeScope
from .origin_scope import OriginScope
from .siblings_scope import SiblingsScope

Scope = CumulativeScope | SiblingsScope | OriginScope
