import uuid
from dataclasses import dataclass

from tidipy import composer, Resolver


@dataclass
class Hey:
    age: int


@dataclass
class Animal:
    name: str


@composer
def hey() -> Hey:
    return Hey(17)


@composer(scope_type='tenant')
def animal() -> Animal:
    return Animal(name='Henk')


@dataclass
class User:
    id: str


@composer(scope_type='request')
def user() -> User:
    return User(id='user')


@composer(scope_type='transient')
def a_random_string() -> str:
    return str(uuid.uuid4())
