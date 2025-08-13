"""Scopes control which members contribute to an aggregation.

:mod:`Aggregation functions <atoti.agg>` need a scope to know how to aggregate measures.
On the other hand, a scope cannot be passed when aggregating table columns or column operations: their aggregation will start from the facts.
"""

from .cumulative_scope import CumulativeScope as CumulativeScope
from .origin_scope import OriginScope as OriginScope
from .siblings_scope import SiblingsScope as SiblingsScope
