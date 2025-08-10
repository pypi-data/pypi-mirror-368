from unittest import TestCase
from test_tidipy import resolver_composition
from test_tidipy.resolver_composition import Buzz

from tidipy import scan, get_resolver, reset


class TestResolver(TestCase):
    def setUp(self) -> None:
        scan(resolver_composition)
        self.resolver = get_resolver()

    def tearDown(self) -> None:
        reset()

    def test_buzz(self):
        result = self.resolver(Buzz)

        self.assertEqual(result, Buzz('My name: Timber'))

    def test_same_instance(self):
        result_1 = self.resolver(Buzz)
        result_2 = self.resolver(Buzz)

        self.assertEqual(id(result_1), id(result_2))
