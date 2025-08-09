from __future__ import annotations

import builtins
import inspect
from typing import TypeVar, Callable, get_type_hints, Optional

from .conditions import parse_conditions
from .dependency import Composer
from .resolver import Resolver
from .scope_type import parse_scope_type

T = TypeVar('T')

FactoryMethod = Callable[[Resolver], T]


def composer(
    factory: Optional[Callable] = None,
    *,
    id: Optional[str] = None,
    scope_type: str = 'root',
    **kwargs: str | set[str]
):
    parsed_scope_type = parse_scope_type(scope_type)

    def inner(func: Callable):
        has_parameter = len(inspect.signature(func).parameters) > 0
        return Composer(
            id=str(builtins.id(func)) if id is None else id,
            scope_type=parsed_scope_type,
            conditions=parse_conditions(**kwargs),
            factory=func if has_parameter else lambda resolve: func(),
            dependency_type=get_type_hints(func).get('return', object)
        )

    if factory is not None:
        return inner(factory)

    return inner
