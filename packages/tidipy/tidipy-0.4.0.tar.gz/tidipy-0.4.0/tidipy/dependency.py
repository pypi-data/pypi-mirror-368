from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Any, Callable

from .conditions import Conditions
from .resolver import Resolver
from .scope_type import ScopeType


class Dependency(ABC):
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_dependency_type(self) -> Type:
        pass

    @abstractmethod
    def get_conditions(self) -> Conditions:
        pass

    @abstractmethod
    def make_concrete(self, resolver: Resolver) -> ConcreteDependency:
        pass

    @abstractmethod
    def supports_storing(self) -> bool:
        pass


@dataclass(frozen=True)
class ConcreteDependency(Dependency):
    id: str
    value: Any
    conditions: Conditions

    def get_id(self) -> str:
        return self.id

    def get_dependency_type(self) -> Type:
        return type(self.value)

    def get_conditions(self) -> Conditions:
        return self.conditions

    def make_concrete(self, resolver: Resolver) -> ConcreteDependency:
        return self

    def supports_storing(self) -> bool:
        return True


@dataclass(frozen=True)
class Composer(Dependency):
    id: str
    scope_type: ScopeType
    conditions: Conditions
    factory: Callable[[Resolver], Any]
    dependency_type: Type

    def get_id(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)

    def get_dependency_type(self) -> Type:
        return self.dependency_type

    def get_conditions(self) -> Conditions:
        return self.conditions

    def make_concrete(self, resolver: Resolver) -> ConcreteDependency:
        return ConcreteDependency(
            id=self.id,
            conditions=self.conditions,
            value=self.factory(resolver)
        )

    def supports_storing(self) -> bool:
        return self.scope_type.supports_storing()
