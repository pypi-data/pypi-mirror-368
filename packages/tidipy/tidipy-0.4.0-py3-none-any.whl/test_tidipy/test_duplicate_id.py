from unittest import TestCase

from test_tidipy import duplicate_id_composition
from tidipy import scan, reset


class TestDuplicateId(TestCase):
    def tearDown(self) -> None:
        reset()

    def test_duplicate_id(self):
        with self.assertRaises(Exception):
            scan(duplicate_id_composition)
