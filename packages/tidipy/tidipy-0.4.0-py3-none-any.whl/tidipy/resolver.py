from __future__ import annotations

from typing import TypeVar, Type, Callable, Any, Optional

from tidipy.dependency_bag import DependencyBag
from tidipy.scope_context import ScopeContext

T = TypeVar('T')


class Resolver:
    def __init__(self, context: ScopeContext, parent: Optional[Resolver], dependency_bag: DependencyBag):
        self._context = context
        self._parent = parent
        self._dependency_bag = dependency_bag

    def with_context(self, context: ScopeContext) -> Resolver:
        return Resolver(context=context, parent=self._parent, dependency_bag=self._dependency_bag)

    def _get(
        self,
        dependency_type: Type,
        dependency_id: Optional[str],
        context: ScopeContext
    ) -> Any:
        result = self._dependency_bag.find(
            dependency_type,
            dependency_id,
            self.with_context(context),
            context
        )
        if result is not None:
            return result

        if self._parent is None:
            raise Exception(f'No candidate for type {dependency_type}')

        return self._parent._get(dependency_type, dependency_id, context)

    def __call__(self, dependency_type: Type[T], id=None) -> T:
        return self._get(dependency_type, dependency_id=id, context=self._context)
