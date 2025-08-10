from unittest import TestCase
from test_tidipy import scope_composition

from test_tidipy.scope_composition import Animal, Hey, User

from tidipy import scan, get_resolver, ensure_scope, clear_scope, reset


class TestScope(TestCase):
    def setUp(self) -> None:
        scan(scope_composition)

    def tearDown(self) -> None:
        reset()

    def test_cannot_access_in_root_scope(self):
        resolver = get_resolver()
        with self.assertRaises(Exception):
            resolver(Animal)

    def test_cannot_get_root_scope_with_other_scope(self):
        with self.assertRaises(Exception):
            ensure_scope(scope_id='root', scope_type='transient')

    def test_cannot_get_root_scope_with_parent(self):
        with self.assertRaises(Exception):
            ensure_scope(scope_id='root', scope_type='root', parent_id='other')

    def test_cannot_get_scope_with_nonexisting_parent(self):
        with self.assertRaises(Exception):
            ensure_scope(scope_id='hey', scope_type='hey', parent_id='non-existant')

    def test_create_scope(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')
        resolver = get_resolver('tenant-a')
        result = resolver(Animal)

        self.assertEqual(Animal(name='Henk'), result)

    def test_ensure_scope(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')
        resolver = get_resolver('tenant-a')
        result = resolver(Animal)

        self.assertEqual(Animal(name='Henk'), result)

    def test_ensure_twice(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')
        ensure_scope(scope_id='tenant-a', scope_type='tenant')

        resolver = get_resolver('tenant-a')
        result = resolver(Animal)

        self.assertEqual(Animal(name='Henk'), result)

    def test_ensure_with_other_type(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')

        with self.assertRaises(Exception):
            ensure_scope(scope_id='tenant-a', scope_type='iets')

    def test_destroy_scope(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')
        clear_scope(scope_id='tenant-a')

        with self.assertRaises(Exception):
            get_resolver('tenant-a')

    def test_can_access_root_scope_from_child(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')
        resolver = get_resolver('tenant-a')

        result = resolver(Hey)

        resolved_from_root = get_resolver()(Hey)

        self.assertEqual(Hey(age=17), result)
        self.assertEqual(id(result), id(resolved_from_root))

    def test_can_access_root_scope_after_clearing(self):
        clear_scope('root')
        resolver = get_resolver()

        result = resolver(Hey)

        self.assertEqual(Hey(age=17), result)

    def test_clear_root_scope(self):
        first_object = get_resolver()(Hey)
        clear_scope('root')
        second_object = get_resolver()(Hey)

        self.assertNotEqual(id(first_object), id(second_object))


    def test_cannot_ensure_parent_scope_with_context_after_nesting(self):
        ensure_scope(scope_id='parent', scope_type='parent')
        ensure_scope(scope_id='child', scope_type='child', parent_id='parent')

        with self.assertRaises(Exception):
            ensure_scope(scope_id='parent', scope_type='parent', context={'a': 'b'})

    def test_can_ensure_root_scope_after_clearing(self):
        ensure_scope(scope_id='parent', scope_type='parent')
        ensure_scope(scope_id='child', scope_type='child', parent_id='parent')
        clear_scope('parent')
        try:
            ensure_scope(scope_id='parent', scope_type='parent', context={'a': 'b'})
        except Exception:
            self.fail()

    def test_nested_scopes(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')
        ensure_scope(scope_id='request-b', scope_type='request', parent_id='tenant-a')
        resolver = get_resolver('request-b')

        user_result = resolver(User)
        hey_result = resolver(Hey)

        self.assertEqual(User(id='user'), user_result)
        self.assertEqual(Hey(age=17), hey_result)

    def test_destroy_child_scopes(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')
        ensure_scope(scope_id='request-b', scope_type='request', parent_id='tenant-a')
        clear_scope('tenant-a')

        with self.assertRaises(Exception):
            get_resolver('request-b')

    def test_cannot_nest_same_type(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')

        with self.assertRaises(Exception):
            ensure_scope(scope_id='tenant-b', scope_type='tenant', parent_id='tenant-a')

    def test_illegal_ensures(self):
        with self.assertRaises(Exception):
            ensure_scope(scope_id='tenant-b', scope_type='root')
        with self.assertRaises(Exception):
            ensure_scope(scope_id='root', scope_type='iets')
        with self.assertRaises(Exception):
            ensure_scope(scope_id='root', scope_type='root', parent_id='iets')
        with self.assertRaises(Exception):
            ensure_scope(scope_id='request-a', scope_type='transient')

    def test_cannot_create_child_scope_of_same_type(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')

        with self.assertRaises(Exception):
            ensure_scope(scope_id='tenant-b', scope_type='tenant', parent_id='tenant-a')

    def test_cannot_nest_scope_of_same_type(self):
        ensure_scope(scope_id='tenant-a', scope_type='tenant')
        ensure_scope(scope_id='request', scope_type='request', parent_id='tenant-a')

        with self.assertRaises(Exception):
            ensure_scope(scope_id='tenant-b', scope_type='tenant', parent_id='request')

    def test_conflicting_scope_types(self):
        ensure_scope(scope_id='x', scope_type='tenant')

        with self.assertRaises(Exception):
            ensure_scope(scope_id='x', scope_type='request')

    def test_transient_dependencies_are_not_stored(self):
        resolver = get_resolver()

        self.assertNotEqual(resolver(str), resolver(str))
