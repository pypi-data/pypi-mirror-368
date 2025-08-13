from collections import defaultdict
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import final


@final
@dataclass(frozen=True, kw_only=True)
class _Report:
    counts: dict[type | None, int] = field(
        default_factory=lambda: defaultdict(lambda: 0)
    )
    durations: dict[type | None, float] = field(
        default_factory=lambda: defaultdict(lambda: 0)
    )


_CHECK_DEFAULT = True


@final
@dataclass(frozen=True, kw_only=True)
class _Context:
    check: bool = _CHECK_DEFAULT
    report: _Report = field(default_factory=_Report)


_CONTEXT_VAR: ContextVar[_Context | None] = ContextVar(
    "atoti_mapping_lookup", default=None
)


@contextmanager
def mapping_lookup(*, check: bool) -> Generator[_Report, None, None]:
    """Create a context customizing the behavior of :class:`~collections.abc.Mapping` lookups.

    A mapping lookup is calling the `Mapping.__getitem__()` method by doing ``mapping[key]``.

    The mappings affected by this context are:

    * :class:`~atoti.distribution.clusters.Clusters`.
    * :class:`~atoti.cubes.Cubes`.
    * :class:`~atoti.hierarchies.Hierarchies`.
    * :class:`~atoti.levels.Levels`.
    * :class:`~atoti.measures.Measures`.
    * :class:`~atoti.distribution.query_cubes.QueryCubes`.
    * :class:`~atoti.Table`'s columns.
    * :class:`~atoti.tables.Tables`.

    Args:
        check:
            * If ``True``, passing a key that does have a corresponding value in the mapping will raise a `KeyError`.
              This is the default behavior outside of this context.

            * If ``False``, keys will not be checked, saving a roundtrip with the server.

              This mode is less safe since incorrect keys will not be caught immediately.
              Besides, the errors that will be raised down the chain may have less explicit messages.

              The main use cases for this mode are:

              * To get a reference to an object before it is actually defined in the data model.
                For instance, it can be used to define :attr:`~atoti.tables.Tables.restrictions` before tables are created.
              * To improve performance when defining the data model or inside a :func:`~atoti.tables.Tables.data_transaction()` by reducing roundtrips to the server when the looked up keys are known to be correct.
                This is especially impactful when using :meth:`atoti.Session.connect` with a remote *url* since latency will not be negligible.

                :data:`__debug__` is a good argument to pass for this use case since it will most likely be:

                * ``True`` during prototyping and testing where good developer experience is important.
                * ``False`` in production where performance matters more.

              In this mode, keys must be unambiguous:

              * For :class:`~atoti.levels.Levels`, this means that the syntax ``l[level_name]`` cannot be used since multiple dimensions or hierarchies could have a level named ``level_name`` and the server cannot be used to ensure unicity and to return the corresponding dimension and hierarchy names.
                For the same reason, ``l[hierarchy_name, level_name]`` cannot be used either.
                Only ``l[dimension_name, hierarchy_name, level_name]`` is accepted.
              * For :class:`~atoti.hierarchies.Hierarchies`, only ``h[dimension_name, hierarchy_name]`` is accepted.

    .. doctest::
        :hide:

        >>> session = getfixture("default_session")

    >>> table = session.create_table(
    ...     "Example",
    ...     data_types={
    ...         "Continent": "String",
    ...         "Country": "String",
    ...         "Population": "int",
    ...     },
    ...     keys={"Continent", "Country"},
    ... )
    >>> cube = session.create_cube(table)
    >>> l, m = cube.levels, cube.measures

    Lookups are checked by default:

    >>> l["Country"].name  # This level exists
    'Country'
    >>> l["City"].name  # This level does not exist
    Traceback (most recent call last):
        ...
    KeyError: 'City'

    Unchecked lookups require unambiguous keys:

    >>> with tt.mapping_lookup(check=False):
    ...     l["Example", "Country", "Country"].name
    'Country'
    >>> with tt.mapping_lookup(check=False):
    ...     l["Country", "Country"].name
    Traceback (most recent call last):
        ...
    ValueError: Cannot use ambiguous key `('Country', 'Country')` when mapping lookup is unchecked. Pass a `(str, str, str)` instead.
    >>> with tt.mapping_lookup(check=False):
    ...     l["Country"].name
    Traceback (most recent call last):
        ...
    ValueError: Cannot use ambiguous key `Country` when mapping lookup is unchecked. Pass a `(str, str, str)` instead.

    Warning:
        What is won in performance is lost in safety since incorrect keys will go unnoticed:

        >>> with tt.mapping_lookup(check=False):
        ...     city_level = l["Example", "City", "City"]  # This level does not exist
        ...     city_level.dimension, city_level.hierarchy, city_level.name
        ('Example', 'City', 'City')

    Unchecked lookup results can be used to construct objects that do not require a request to the server such as conditions:

    >>> city_level == "Rome"
    l['Example', 'City', 'City'] == 'Rome'
    >>> city_level.isin("Barcelona", "Paris")
    l['Example', 'City', 'City'].isin('Barcelona', 'Paris')

    But accessing a property (or calling a method) on an object looked up with an incorrect key will raise an error if this function makes a request to the server:

    >>> city_level.order  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    py4j.protocol.Py4JError: An error occurred ...
    ...

    Note:
        Iteration, the ``in`` operator, and the :meth:`~dict.get` method are not impacted by this context:

        >>> with tt.mapping_lookup(check=False):
        ...     sorted(l)
        [('Example', 'Continent', 'Continent'), ('Example', 'Country', 'Country')]
        >>> with tt.mapping_lookup(check=False):
        ...     "Continent" in l, "Country" in l, "City" in l
        (True, True, False)
        >>> with tt.mapping_lookup(check=False):
        ...     l.get("Country").name, l.get("City"), l.get("City", default="fallback")
        ('Country', None, 'fallback')

    This context can be nested.
    Nesting can be used inside functions to defensively force the mode they need regardless of the outer context:

    >>> def _get_level_or_raise_error(cube, level_name):
    ...     with tt.mapping_lookup(check=True):
    ...         # Ambiguous keys only work with checked lookups.
    ...         return cube.levels[level_name]
    >>> with tt.mapping_lookup(check=False):
    ...     _get_level_or_raise_error(cube, "Country").name
    'Country'

    Unchecked lookups can be chained:

    >>> with tt.mapping_lookup(check=False):
    ...     session.tables["Unexisting table"]["Unexisting column"] == 0
    t['Unexisting table']['Unexisting column'] == 0

    Tip:
        When *check* is ``True``, the context's target reports, per :class:`~collections.abc.Mapping` class, how many lookups occurred and how long they took.
        The sum of these metrics is added under the ``None`` key once the context exits.
        This report can be used to decide if migrating to unchecked lookups is worth it:

        >>> from atoti.levels import Levels
        >>> from atoti.measures import Measures
        >>> with tt.mapping_lookup(check=True) as report:
        ...     _ = l["Continent"]
        ...     assert report.counts[Levels] == 1
        ...     first_duration = report.durations[Levels]
        ...     _ = l["Country"]
        ...     assert report.counts[Levels] == 2
        ...     assert report.durations[Levels] > first_duration
        ...     _ = m["Population.SUM"]
        >>> {**report.counts}
        {<class 'atoti.levels.Levels'>: 2, <class 'atoti.measures.Measures'>: 1, None: 3}
        >>> report.durations[None] == report.durations[Levels] + report.durations[
        ...     Measures
        ... ]
        True

    """
    context = _Context(check=check)
    token = _CONTEXT_VAR.set(context)
    try:
        yield context.report
    finally:
        _CONTEXT_VAR.reset(token)
        context.report.counts[None] = sum(context.report.counts.values())
        context.report.durations[None] = sum(context.report.durations.values())
