from unittest import TestCase

from test_tidipy import autocompose_composition
from test_tidipy.autocompose_composition import PointWrapper, Point, PointWrapperWrapper, EmptyInit
from tidipy import scan, get_resolver, reset, auto_compose, ensure_scope


class TestAutoCompose(TestCase):
    def setUp(self) -> None:
        scan(autocompose_composition)

    def tearDown(self) -> None:
        reset()

    def test_auto_compose(self):
        auto_compose(PointWrapperWrapper)
        resolver = get_resolver()
        result = resolver(PointWrapperWrapper)

        self.assertEqual(PointWrapper(point=Point(x=3, y=4)), result.point_wrapper)

    def test_auto_compose_with_scope_type(self):
        auto_compose(PointWrapperWrapper, scope_type='tenant')
        resolver = get_resolver()
        ensure_scope('tenant-a', scope_type='tenant')
        tenant_resolver = get_resolver('tenant-a')

        with self.assertRaises(Exception):
            resolver(PointWrapperWrapper)
        self.assertEqual(PointWrapper(point=Point(x=3, y=4)), tenant_resolver(PointWrapperWrapper).point_wrapper)

    def test_auto_compose_with_id(self):
        auto_compose(PointWrapper, id='auto-composed')
        resolver = get_resolver()

        result = resolver(PointWrapper, id='auto-composed')

        self.assertEqual(PointWrapper(point=Point(x=1, y=2)), result)

    def test_duplicate_ids(self):
        auto_compose(str, id='some_id')

        with self.assertRaises(Exception):
            auto_compose(str, id='some_id', scope_type='else')

    def test_empty_init(self):
        auto_compose(EmptyInit)
        resolver = get_resolver()
        result = resolver(EmptyInit)

        self.assertEqual(result.hey(), 'hey')
