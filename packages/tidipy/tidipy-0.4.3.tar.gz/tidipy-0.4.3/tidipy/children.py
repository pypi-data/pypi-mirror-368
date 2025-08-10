from typing import Protocol, Optional, TypeVar, Generic


class HasId(Protocol):
    def get_id(self) -> str: ...

T = TypeVar('T', bound=HasId)


class Children(Generic[T]):
    def __init__(self, value: T, children: dict[str, T]):
        self._value = value
        self._children = children


    def add_child(
        self,
        child: T
    ):
        self._children[child.get_id()] = child

    def find_descendant(self, node_id: str) -> Optional[T]:
        if node_id == self._value.get_id():
            return self._value

        for child_id, child in self._children.items():
            result = child.find_scope(node_id)
            if result is not None:
                return result

        return None

    def remove_descendant(self, node_id: str) -> None:
        if node_id in self._children:
            self._children.pop(node_id)

        for child_id, child in self._children.items():
            child.remove_scope(node_id)
