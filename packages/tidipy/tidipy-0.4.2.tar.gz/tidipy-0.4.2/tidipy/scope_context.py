from __future__ import annotations


class ScopeContext:
    def __init__(self, values: dict[str, str]):
        self._values = values

    @staticmethod
    def empty() -> ScopeContext:
        return ScopeContext({})

    def add(self, context: ScopeContext) -> ScopeContext:
        if not set(context.values().keys()).isdisjoint(set(self._values.keys())):
            raise Exception('Can only add values to scope context, not override values')

        return ScopeContext({**self._values, **context.values()})

    def part_of(self, context: ScopeContext) -> bool:
        return all(self._values[key] == context._values[key] for key in self._values.keys())

    def values(self) -> dict[str, str]:
        return self._values
