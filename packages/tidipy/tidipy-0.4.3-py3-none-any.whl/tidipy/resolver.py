from abc import abstractmethod
from typing import Type, TypeVar, Optional

T = TypeVar('T')

class Resolver:
    @abstractmethod
    def __call__(self, dependency_type: Type[T], id: Optional[str] = None) -> T:
        ...
