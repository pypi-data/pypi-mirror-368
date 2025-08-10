from __future__ import annotations


class ScopeContext:
    def __init__(self, values: dict[str, str]):
        self._values = values

    @staticmethod
    def empty() -> ScopeContext:
        return ScopeContext({})

    def add(self, context: ScopeContext) -> ScopeContext:
        common_keys = set(context.values().keys()).intersection(set(self._values.keys()))

        if any(self._values[key] != context.values()[key] for key in common_keys):
            raise Exception('Can only add values to scope context, not override values')

        return ScopeContext({**self._values, **context.values()})

    def part_of(self, context: ScopeContext) -> bool:
        return context.add(self) == context

    def __eq__(self, other) -> bool:
        if not isinstance(other, ScopeContext):
            return False

        return self._values == other.values()

    def values(self) -> dict[str, str]:
        return self._values
