from abc import ABC, abstractmethod
from dataclasses import dataclass


class ScopeType(ABC):
    @abstractmethod
    def supports_storing(self) -> bool:
        pass


@dataclass(frozen=True)
class RootType(ScopeType):
    def supports_storing(self) -> bool:
        return True


@dataclass(frozen=True)
class Transient(ScopeType):
    def supports_storing(self) -> bool:
        return False


@dataclass(frozen=True)
class CustomScope(ScopeType):
    scope_type: str

    def supports_storing(self) -> bool:
        return True


def parse_scope_type(value: str) -> ScopeType:
    if value == 'root':
        return RootType()
    if value == 'transient':
        return Transient()

    return CustomScope(value)
