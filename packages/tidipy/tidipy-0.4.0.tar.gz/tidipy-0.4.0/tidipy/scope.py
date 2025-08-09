from __future__ import annotations

from typing import TypeVar, Optional

from .children import Children
from .dependency import Composer
from .dependency_bag import DependencyBag
from .resolver import Resolver
from .scope_context import ScopeContext
from .scope_type import ScopeType, Transient

T = TypeVar('T')


class Scope:
    def __init__(
        self,
        scope_id: str,
        scope_type: ScopeType,
        composers: set[Composer],
        context: ScopeContext,
        parent: Optional[Scope] = None
    ):
        self._scope_id = scope_id
        self._parent = parent
        self._children: Children[Scope] = Children(self, {})
        self._scope_type = scope_type
        self._composers = composers
        self._context = context
        self._resolver = self._create_resolver()
        self._validate()

    def _create_resolver(self) -> Resolver:
        return Resolver(
            context=self._context,
            parent=self._parent.resolver() if self._parent is not None else None,
            dependency_bag=DependencyBag.from_dependencies({
                composer
                for composer in self._composers
                if not composer.scope_type.supports_storing() or composer.scope_type == self._scope_type
            })
        )

    def _ancestor_has_type(self, scope_type: ScopeType) -> bool:
        if self._parent is None:
            return False

        if self._parent._scope_type == scope_type:
            return True

        return self._parent._ancestor_has_type(scope_type)

    def _validate(self):
        if self._ancestor_has_type(self._scope_type):
            raise Exception('Ancestor already has a scope of this type')
        if self._scope_type == Transient():
            raise Exception('Scopes can not have type transient')

    def get_id(self) -> str:
        return self._scope_id

    def add_scope(
        self,
        scope_id: str,
        scope_type: ScopeType,
        context: ScopeContext
    ):
        self._children.add_child(
            Scope(
                scope_id=scope_id,
                parent=self,
                scope_type=scope_type,
                composers=self._composers,
                context= context.add(self._context)
            )
        )

    def find_scope(self, scope_id: str) -> Optional[Scope]:
        return self._children.find_descendant(scope_id)

    def remove_scope(self, scope_id: str) -> None:
        self._children.remove_descendant(scope_id)

    def matches(self, scope_type: ScopeType, parent_id: Optional[str], context: Optional[ScopeContext]) -> bool:
        if self._scope_type != scope_type:
            return False
        if self._parent is None and parent_id is not None:
            return False
        if self._parent is not None and self._parent.get_id() != parent_id:
            return False
        if context is not None and not context.part_of(self._context):
            return False

        return True

    def resolver(self) -> Resolver:
        return self._resolver
