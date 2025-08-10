from dataclasses import dataclass

from tidipy.scope_context import ScopeContext


@dataclass(frozen=True)
class ContextFilterElement:
    key: str
    one_of_values: set[str]

    def is_fulfilled_by(self, context: ScopeContext) -> bool:
        if self.key not in context.values():
            return True

        return context.values()[self.key] in self.one_of_values


@dataclass(frozen=True)
class ContextFilter:
    elements: set[ContextFilterElement]

    def is_fulfilled_by(self, context: ScopeContext) -> bool:
        return all(element.is_fulfilled_by(context) for element in self.elements)

    def is_empty(self) -> bool:
        return len(self.elements) == 0


def parse_context_filter(**kwargs) -> ContextFilter:
    return ContextFilter(
            elements={
                ContextFilterElement(
                    key=key,
                    one_of_values=frozenset(value) if isinstance(value, set) else frozenset({value})  # type: ignore
                )
                for key, value in kwargs.items()
            }
        )
