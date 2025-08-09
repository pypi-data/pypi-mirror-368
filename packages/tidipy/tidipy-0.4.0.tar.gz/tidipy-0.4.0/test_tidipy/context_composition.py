from abc import ABC, abstractmethod

from tidipy import composer, Resolver


class StringGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass


class TimberGenerator(StringGenerator):
    def generate(self) -> str:
        return 'Timber'


class HelloGenerator(StringGenerator):
    def generate(self) -> str:
        return 'Hello'


class App:
    def __init__(self, generator: StringGenerator):
        self._generator = generator

    def generate(self) -> str:
        return self._generator.generate()


@composer(environment='prod')
def timber() -> TimberGenerator:
    return TimberGenerator()


@composer(environment='test')
def hello() -> HelloGenerator:
    return HelloGenerator()


@composer
def app(resolve: Resolver) -> App:
    return App(resolve(StringGenerator))
