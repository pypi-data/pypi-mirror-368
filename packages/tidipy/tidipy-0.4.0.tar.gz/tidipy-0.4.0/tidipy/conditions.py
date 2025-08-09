from dataclasses import dataclass


@dataclass(frozen=True)
class Condition:
    key: str
    one_of_values: set[str]

    def is_fulfilled_by(self, value_map: dict[str, str]) -> bool:
        if self.key not in value_map:
            return True

        return value_map[self.key] in self.one_of_values


@dataclass(frozen=True)
class Conditions:
    conditions: set[Condition]

    def is_fulfilled_by(self, value_map: dict[str, str]) -> bool:
        return all(condition.is_fulfilled_by(value_map) for condition in self.conditions)


def parse_conditions(**kwargs) -> Conditions:
    return Conditions(
            conditions={
                Condition(
                    key=key,
                    one_of_values=frozenset(value) if isinstance(value, set) else frozenset({value})  # type: ignore
                )
                for key, value in kwargs.items()
            }
        )
