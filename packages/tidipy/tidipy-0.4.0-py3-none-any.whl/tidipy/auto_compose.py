import builtins
import inspect
from typing import Type, Optional

from .auto_factory import AutoFactory
from .dependency import Composer
from .conditions import parse_conditions
from .composer_repository import ComposerRepository
from .scope_type import parse_scope_type


def auto_compose(
    dependency_type: Type,
    *,
    id: Optional[str] = None,
    scope_type: str = 'root',
    **kwargs
):
    if not inspect.isclass(dependency_type):
        raise ValueError
    factory = AutoFactory(dependency_type)
    composer = Composer(
            id=str(builtins.id(dependency_type)) if id is None else id,
            scope_type=parse_scope_type(scope_type),
            conditions=parse_conditions(**kwargs),
            dependency_type=dependency_type,
            factory=factory
        )
    ComposerRepository.add_composer(composer)
