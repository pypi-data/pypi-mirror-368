from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from functools import reduce

from typing_extensions import assert_type

from .._constant import Constant
from .._identification import (
    HasIdentifier,
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
)
from .._measure.switch_on_measure import SwitchOnMeasure
from .._measure_convertible import (
    MeasureCondition,
    MeasureConvertible,
    MeasureConvertibleIdentifier,
    MeasureOperation,
    VariableMeasureConvertible,
    is_variable_measure_convertible,
)
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from .._operation import Condition as _Condition, Operation, RelationalCondition
from .where import where


def _create_condition(
    *,
    subject: VariableMeasureConvertible,
    target: MeasureConvertible | None,
) -> MeasureCondition:
    if isinstance(subject, _Condition):
        raise TypeError(
            f"Cannot use a `{type(subject).__name__}` as a `{switch.__name__}()` subject.",
        )
    if isinstance(target, _Condition):
        raise TypeError(
            f"Cannot use a `{type(target).__name__}` as a `{switch.__name__}()` target.",
        )
    match subject:
        case HasIdentifier():
            if isinstance(subject._identifier, HierarchyIdentifier):
                raise NotImplementedError(
                    f"{subject._identifier} was passed but conditions on hierarchies are not supported."
                )

            condition_subject: (
                LevelIdentifier
                | MeasureIdentifier
                | MeasureCondition
                | MeasureOperation
            ) = subject._identifier
        case _:
            condition_subject = subject

    match target:
        case None:
            condition_target: (
                Constant | MeasureConvertibleIdentifier | MeasureOperation | None
            ) = None
        case HasIdentifier():
            condition_target = target._identifier
        case Operation():
            condition_target = target
        case _:
            assert_type(target, Constant)
            condition_target = target

    return RelationalCondition(
        subject=condition_subject, operator="==", target=condition_target
    )


def switch(
    subject: VariableMeasureConvertible,
    cases: Mapping[
        MeasureConvertible | None | AbstractSet[MeasureConvertible | None],
        MeasureConvertible,
    ],
    /,
    *,
    default: MeasureConvertible | None = None,
) -> MeasureDefinition:
    """Return a measure equal to the value of the first case for which *subject* is equal to the case's key.

    *cases*'s values and *default* must either be all numerical, all boolean or all objects.

    Args:
        subject: The measure or level to compare to *cases*' keys.
        cases: A mapping from keys to compare with *subject* to the values to return if the comparison is ``True``.
        default: The measure to use when none of the *cases* matched.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["Id", "City", "Value"],
        ...     data=[
        ...         (0, "Paris", 1.0),
        ...         (1, "Paris", 2.0),
        ...         (2, "London", 3.0),
        ...         (3, "London", 4.0),
        ...         (4, "Paris", 5.0),
        ...         (5, "Singapore", 7.0),
        ...         (6, "NYC", 2.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys={"Id"}, table_name="Switch example")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Continent"] = tt.switch(
        ...     l["City"],
        ...     {
        ...         frozenset({"Paris", "London"}): "Europe",
        ...         "Singapore": "Asia",
        ...         "NYC": "North America",
        ...     },
        ... )
        >>> cube.query(m["Continent"], levels=[l["City"]])
                       Continent
        City
        London            Europe
        NYC        North America
        Paris             Europe
        Singapore           Asia
        >>> m["Europe & Asia value"] = tt.agg.sum(
        ...     tt.switch(
        ...         m["Continent"],
        ...         {frozenset({"Europe", "Asia"}): m["Value.SUM"]},
        ...         default=0.0,
        ...     ),
        ...     scope=tt.OriginScope({l["Id"], l["City"]}),
        ... )
        >>> cube.query(m["Europe & Asia value"], levels=[l["City"]])
                  Europe & Asia value
        City
        London                   7.00
        NYC                       .00
        Paris                    8.00
        Singapore                7.00
        >>> cube.query(m["Europe & Asia value"])
          Europe & Asia value
        0               22.00

    See Also:
        :func:`atoti.where`.
    """
    if isinstance(subject, HasIdentifier) and isinstance(
        subject._identifier,
        LevelIdentifier,
    ):
        flatten_cases: dict[MeasureConvertible | None, MeasureConvertible] = {}

        for key, value in cases.items():
            if isinstance(key, AbstractSet):
                for element in key:
                    flatten_cases[element] = value
            else:
                flatten_cases[key] = value

        constant_cases: dict[Constant | None, MeasureConvertible] = {
            key: value
            for key, value in flatten_cases.items()
            if not is_variable_measure_convertible(key)
        }

        if len(constant_cases) == len(flatten_cases):
            return SwitchOnMeasure(
                _subject=subject._identifier,
                _cases={
                    key: convert_to_measure_definition(value)
                    for key, value in constant_cases.items()
                    if key is not None
                },
                _default=None
                if default is None
                else convert_to_measure_definition(default),
                _above_level=convert_to_measure_definition(cases[None])
                if None in cases
                else None,
            )

    # If the subject is a measure, we return a where measure
    condition_to_measure: dict[
        VariableMeasureConvertible,
        MeasureConvertible,
    ] = {}
    for values, measure in cases.items():
        if isinstance(values, AbstractSet):
            condition_to_measure[
                reduce(
                    lambda a, b: a | b,
                    [
                        _create_condition(subject=subject, target=value)
                        for value in values
                    ],
                )
            ] = measure
        else:
            condition_to_measure[_create_condition(subject=subject, target=values)] = (
                measure
            )
    return where(condition_to_measure, default=default)
