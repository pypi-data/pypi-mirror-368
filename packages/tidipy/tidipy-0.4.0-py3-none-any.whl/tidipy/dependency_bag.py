from __future__ import annotations

from typing import Optional, Type, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .resolver import Resolver
    from .dependency import Dependency
from .scope_context import ScopeContext


class DependencyBag:
    def __init__(self, dependencies: dict[str, Dependency]):
        self._dependencies = dependencies

    @staticmethod
    def from_dependencies(dependencies: Iterable[Dependency]) -> DependencyBag:
        return DependencyBag({dependency.get_id(): dependency for dependency in dependencies})

    def _get_candidates(
        self,
        dependency_type: Type,
        dependency_id: Optional[str],
        scope_context: ScopeContext
    ) -> list[Dependency]:
        candidates = [
            dependency
            for dependency in self._dependencies.values()
            if issubclass(dependency.get_dependency_type(), dependency_type)
               and dependency.get_conditions().is_fulfilled_by(scope_context.values())
        ]
        if dependency_id is not None:
            candidates = [dependency for dependency in candidates if dependency.get_id() == dependency_id]

        return candidates

    def find(
        self,
        dependency_type: Type,
        dependency_id: Optional[str],
        resolver: Resolver,
        scope_context: ScopeContext
    ) -> Optional[Dependency]:
        candidates = self._get_candidates(dependency_type, dependency_id, scope_context)

        if len(candidates) == 0:
            return None
        if len(candidates) > 1:
            raise Exception(f'More than 1 candidate for type {dependency_type}')

        dependency = next(iter(candidates))
        concrete = dependency.make_concrete(resolver)

        if dependency.supports_storing():
            self._dependencies[dependency.get_id()] = concrete

        return concrete.value
