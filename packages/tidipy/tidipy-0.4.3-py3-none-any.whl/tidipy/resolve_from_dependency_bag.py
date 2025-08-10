from __future__ import annotations

from typing import TypeVar, Type, Optional

from tidipy.dependency_bag import DependencyBag
from tidipy.resolver import Resolver

T = TypeVar('T')


class ResolveFromDependencyBag(Resolver):
    def __init__(self, parent: Optional[ResolveFromDependencyBag], dependency_bag: DependencyBag):
        self._parent = parent
        self._dependency_bag = dependency_bag

    def __call__(self, dependency_type: Type[T], id: Optional[str] = None) -> T:
        result = self._dependency_bag.find(dependency_type, id, self)
        if result is not None:
            return result

        if self._parent is None:
            raise Exception(f'No candidate for type {dependency_type}')

        return self._parent(dependency_type, id)
