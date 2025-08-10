from dataclasses import dataclass

from tidipy import composer, Resolver


@composer(id='timber')
def my_name() -> str:
    return 'Timber'


@composer
def other_name() -> str:
    return 'Benji'


@dataclass
class Buzz:
    description: str


@composer
def buzz(resolve: Resolver) -> Buzz:
    name = resolve(str, id='timber')
    return Buzz(description=f'My name: {name}')
