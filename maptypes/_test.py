"""
This module defines tests for the `Map` protocol and a function to run them
(`test_map_type`) for a given implementation type and namespace.

Any tests added here will be ran for all implementations of `Map`.
"""

from typing import Type

from unittest_extensions import args, TestCase

from maptypes.map import Map


def test_map_type(map_type: Type[Map], namespace: dict):
    """
    Define all `Map` API tests for the given map type in the given namespace by
    defining a series of test classes.

    Running `test_map_type(MapType, locals())` in a module is enough to run all
    tests for the `Map` protocol. Passing in the `locals()` namespace will
    also make available to the module-level all tests classes.
    The base test class named `TestMapType` (e.g. for the above example) can
    be used to define extra test cases specific to a certain implementation.
    """
    base_cls_name = _cls_name(map_type)
    iterator_cls_name = _cls_name(map_type, True)
    namespace[base_cls_name] = create_map_base_test_class(map_type)
    namespace[iterator_cls_name] = create_map_iterator_base_test_class(map_type)

    def _create_map_test_class(suffix, base_test_class):
        cls_name = base_cls_name + suffix
        namespace[cls_name] = type(
            cls_name,
            (namespace[base_cls_name], base_test_class),
            {},
        )

    def _create_map_iterator_test_class(suffix, base_test_class):
        cls_name = base_cls_name + suffix
        namespace[cls_name] = type(
            cls_name,
            (namespace[iterator_cls_name], base_test_class),
            {},
        )

    _create_map_test_class("Len", TestLen)
    _create_map_test_class("Iter", TestIter)
    _create_map_test_class("Contains", TestContains)
    _create_map_test_class("SetItem", TestSetItem)
    _create_map_test_class("GetItem", TestGetItem)
    _create_map_test_class("DelItem", TestDelItem)
    _create_map_test_class("Eq", TestEq)
    _create_map_test_class("Get", TestGet)
    _create_map_test_class("GetDefault", TestGetDefault)
    _create_map_test_class("Keys", TestKeys)
    _create_map_test_class("Values", TestValues)
    _create_map_test_class("Items", TestItems)
    _create_map_test_class("Pop", TestPop)
    _create_map_test_class("PopDefault", TestPopDefault)
    _create_map_test_class("Clear", TestClear)
    _create_map_iterator_test_class("KeysIterator", TestKeysIterator)
    _create_map_iterator_test_class("ValuesIterator", TestValuesIterator)
    _create_map_iterator_test_class("ItemsIterator", TestItemsIterator)


def test_sorted_map_type(map_type: Type[Map], namespace: dict):
    """
    Just like `test_map_type` but defines test cases specific to sorted `Map`
    types.
    """
    base_cls_name = _sorted_cls_name(map_type)
    namespace[base_cls_name] = create_sorted_map_base_test_class(map_type)

    def _create_map_test_class(suffix, base_test_class):
        cls_name = base_cls_name + suffix
        namespace[cls_name] = type(
            cls_name, (namespace[base_cls_name], base_test_class), {}
        )

    _create_map_test_class("Iter", TestIterOrder)
    _create_map_test_class("SetItem", TestSetItemDifferentType)
    _create_map_test_class("Keys", TestKeysOrder)
    _create_map_test_class("Values", TestValuesOrder)
    _create_map_test_class("Items", TestItemsOrder)


def create_map_base_test_class(map_type: Type[Map]):
    """
    Create a base test class for a `Map` type.

    The created class inherits from `TestMap` and `unittest_extensions.TestCase`
    and sets the `map_type` class variable to the given map type.
    """
    cls_name = _cls_name(map_type)
    return type(cls_name, (TestMap, TestCase), dict(map_type=map_type))


def create_map_iterator_base_test_class(map_type: Type[Map]):
    """
    Create a base test class for a `MapIterator` type.

    The created class inherits from `TestMapIterator` and `unittest_extensions.TestCase`
    and sets the `map_type` class variable to the given map type.
    """
    cls_name = _cls_name(map_type, True)
    return type(cls_name, (TestMapIterator, TestCase), dict(map_type=map_type))


def create_sorted_map_base_test_class(map_type: Type[Map]):
    """
    Create a base test class for a sorted `Map` type.

    The created class inherits from `TestSortedMap` and `unittest_extensions.TestCase`
    and sets the `map_type` class variable to the given map type.
    """
    cls_name = _cls_name(map_type)
    return type(cls_name, (TestSortedMap, TestCase), dict(map_type=map_type))


def _cls_name(map_type: Type[Map], iterator=False) -> str:
    name = "Test" + map_type.__name__
    name = name + "Iterator" if iterator else name

    return name


def _sorted_cls_name(map_type: Type[Map]) -> str:
    return "TestSorted" + map_type.__name__


class TestMap:
    """
    Defines a setup method, a method to get the map object, a method
    to add an entry to the map and helper methods for quick assertion.

    Inherit from this class (first) and `unittest_extensions.TestCase` (second)
    and define a `map_type` class variable with the type of the map object
    you will test.
    """

    map_type: Map

    def setUp(self):
        self._map = self.map_type()

    def map(self):
        if self._map is None:
            self._map = self.map_type()

        return self._map

    def add_item(self, key, value=None):
        self.map().__setitem__(key, value)

    def assert_result_str(self, result_str, result_instance_check=False):
        if result_instance_check:
            self.assertResultIs(self.map())
        else:
            self.assertResultIsNot(self.map())
        self.assertSequenceEqual(str(self.cachedResult()), result_str, str)

    def assert_unhashable_type(self):
        self.assertResultRaisesRegex(TypeError, "unhashable type")

    def assert_list(self, result_lst):
        self.assertSequenceEqual(self.result(), result_lst, list)


class TestLen(TestMap):
    def subject(self):
        return len(self.map())

    def test_empty_map(self):
        self.assertResult(0)

    def test_non_empty_map(self):
        self.add_item(1, 1)
        self.assertResult(1)


class TestIter(TestMap):
    def subject(self):
        return [key for key in self.map()]

    def test_empty_map(self):
        self.assertEqual(len(self.result()), 0)

    def test_non_empty_map(self):
        self.add_item("key", "value")
        self.assert_list(["key"])

    def test_does_not_mutate_keys(self):
        self.add_item("key", "value")
        for key in self.map():
            key = "new-key"
        self.assertEqual(self.map().__getitem__("key"), "value")


class TestContains(TestMap):
    def subject(self, key):
        return key in self.map()

    @args(1)
    def test_new_key(self):
        self.assertResultFalse()

    @args("key")
    def test_existent_key(self):
        self.add_item("key", "value")
        self.assertResultTrue()

    @args({1})
    def test_unhashable_key_raises(self):
        self.assert_unhashable_type()

    @args((1, {2}))
    def test_unhashable_tuple_item_raises(self):
        self.assert_unhashable_type()

    @args(("key1", "key2"))
    def test_hashable_tuple(self):
        self.assertResultFalse()


class TestGetItem(TestMap):
    def subject(self, key):
        return self.map()[key]

    @args(1)
    def test_new_key_raises(self):
        self.assertResultRaises(KeyError)

    @args({1})
    def test_unhashable_key_raises(self):
        self.assert_unhashable_type()

    @args("key")
    def test_gets_value(self):
        self.add_item("key", "value")
        self.assertResult("value")

    @args("key")
    def test_mutable_value_is_mutated(self):
        lst = [1, 2]
        self.add_item("key", lst)
        lst.append(3)
        self.assertResult([1, 2, 3])

    @args("key2")
    def test_multiple_entries(self):
        self.add_item("key1", 1)
        self.add_item("key2", 2)
        self.assertResult(2)

    @args("key1")
    def test_multiple_entries_2(self):
        self.add_item("key2", 2)
        self.add_item("key1", 1)
        self.assertResult(1)


class TestSetItem(TestMap):
    def subject(self, key, value):
        self.map()[key] = value
        return self.map()[key]

    @args(1, 2)
    def test_new_item(self):
        self.assertResult(2)

    @args({1}, 2)
    def test_unhashable_key_raises(self):
        self.assert_unhashable_type()

    @args("key", "new_value")
    def test_update_value(self):
        self.map()["key"] = "old_value"
        self.assertResult("new_value")

    @args((1, {2}), "value")
    def test_unhashable_tuple_item_raises(self):
        self.assert_unhashable_type()


class TestDelItem(TestMap):
    def subject(self, key):
        del self.map()[key]

        try:
            self.map()[key]
        except KeyError:
            return True
        except Exception as e:
            raise e

    @args(1)
    def test_new_key_raises(self):
        self.assertResultRaises(KeyError)

    @args(1)
    def test_existent_key(self):
        self.add_item(1, 1)
        self.assertResultTrue()

    @args({1})
    def test_unhashable_key_raises(self):
        self.assert_unhashable_type()

    @args((1, {2}))
    def test_unhashable_tuple_item_raises(self):
        self.assert_unhashable_type()


class TestEq(TestMap):
    def subject(self, _map):
        return self.map() == _map

    @args({})
    def test_empty_maps(self):
        self.assertResultTrue()

    @args(1)
    def test_with_non_map(self):
        self.assertResultFalse()

    @args({1: 1})
    def test_with_same_items(self):
        self.add_item(1, 1)
        self.assertResultTrue()

    @args({1: [1, 2]})
    def test_with_equal_items(self):
        self.add_item(1, [1, 2])
        self.assertResultTrue()

    @args({1: 2})
    def test_with_different_value(self):
        self.add_item(1, 1)
        self.assertResultFalse()

    @args({2: 2, 1: 1})
    def test_with_different_order(self):
        self.add_item(1, 1)
        self.add_item(2, 2)
        self.assertResultTrue()


class TestGet(TestMap):
    def subject(self, key):
        return self.map().get(key)

    @args(1)
    def test_new_key_returns_none(self):
        self.assertResultIs(None)

    @args(1)
    def test_existent_key_returns_value(self):
        self.add_item(1, "value")
        self.assertResult("value")

    @args({1})
    def test_unhashable_key_raises(self):
        self.assert_unhashable_type()

    @args((1, {2}))
    def test_unhashable_tuple_item_raises(self):
        self.assert_unhashable_type()


class TestGetDefault(TestMap):
    def subject(self, key, default):
        return self.map().get(key, default)

    @args("key", "default")
    def test_new_key_returns_default(self):
        self.assertResult("default")

    @args("key", 1)
    def test_existent_key_returns_value(self):
        self.add_item("key", 2)
        self.assertResult(2)

    @args({1}, 1)
    def test_unhashable_key_raises(self):
        self.assert_unhashable_type()

    @args((1, {2}), "default")
    def test_unhashable_tuple_item_raises(self):
        self.assert_unhashable_type()


class TestKeys(TestMap):
    def subject(self):
        return [key for key in self.map().keys()]

    def test_empty_map(self):
        self.assertResult([])

    def test_non_empty_map(self):
        self.add_item("key", 1)
        self.assertResult(["key"])


class TestValues(TestMap):
    def subject(self):
        return [v for v in self.map().values()]

    def test_empty_map(self):
        self.assertResult([])

    def test_non_empty_map(self):
        self.add_item(1, "value")
        self.assertResult(["value"])

    def test_mutate_value(self):
        self.add_item(1, [1])
        self.result()[0].append(2)
        self.assertResult([[1, 2]])


class TestItems(TestMap):
    def subject(self):
        return [(k, v) for k, v in self.map().items()]

    def test_empty_map(self):
        self.assertResult([])

    def test_non_empty_map(self):
        self.add_item(1, 1)
        self.assertResult([(1, 1)])

    def test_values_are_mutable(self):
        self.add_item("key", [1, 2])
        [(k, v) for k, v in self.map().items()][0][1].append(3)
        self.assertEqual(self.map()["key"], [1, 2, 3])


class TestPop(TestMap):
    def subject(self, key):
        return self.map().pop(key)

    @args(1)
    def test_new_key_raises(self):
        self.assertResultRaises(KeyError)

    @args(1)
    def test_existent_key(self):
        self.add_item(1, 1)
        self.assertResult(1)

    @args(1)
    def test_pop_removes_item(self):
        self.add_item(1, 1)
        self.result()
        self.assertEqual(self.map().__len__(), 0)

    @args({1})
    def test_unhashable_key_raises(self):
        self.assert_unhashable_type()


class TestPopDefault(TestMap):
    def subject(self, key, default):
        return self.map().pop(key, default)

    @args(1, "default")
    def test_new_key_returns_default(self):
        self.assertResult("default")

    @args(1, "default")
    def test_existent_key_returns_value(self):
        self.add_item(1, "old_value")
        self.assertResult("old_value")


class TestClear(TestMap):
    def subject(self):
        self.map().clear()
        return self.map()

    def test_empty_map(self):
        self.assert_result_str("{}", result_instance_check=True)

    def test_non_empty_map(self):
        self.add_item(1, 1)
        self.assert_result_str("{}", result_instance_check=True)


# DON'T FORGET TO ADD NEW TEST CASES TO test_map_type


class TestMapIterator:
    map_type: Map

    def setUp(self):
        self._map = self.map_type()

    def map(self):
        if self._map is None:
            self._map = self.map_type()

        return self._map

    def add_item(self, key, value=None):
        self.map().__setitem__(key, value)


class TestKeysIterator(TestMapIterator):
    def subject(self):
        return iter(self.map())

    def test_empty_map(self):
        with self.assertRaises(StopIteration):
            next(self.result())

    def test_non_empty_map(self):
        self.add_item("key", "value")
        self.assertEqual(next(self.result()), "key")


class TestValuesIterator(TestMapIterator):
    def subject(self):
        return iter(self.map().values())

    def test_empty_map(self):
        with self.assertRaises(StopIteration):
            next(self.result())

    def test_non_empty_map(self):
        self.add_item("key", "value")
        self.assertEqual(next(self.result()), "value")


class TestItemsIterator(TestMapIterator):
    def subject(self):
        return iter(self.map().items())

    def test_empty_map(self):
        with self.assertRaises(StopIteration):
            next(self.result())

    def test_non_empty_map(self):
        self.add_item("key", "value")
        self.assertEqual(next(self.result()), ("key", "value"))


# DON'T FORGET TO ADD NEW TEST CASES TO test_map_type


class TestSortedMap(TestMap):
    """
    Base class for all cases that test order of the result.
    """


class TestIterOrder(TestSortedMap):
    def subject(self):
        return [key for key in self.map()]

    def test_sorted_order(self):
        self.add_item(5)
        self.add_item(1)
        self.add_item(3)
        self.assert_list([1, 3, 5])


class TestSetItemDifferentType(TestSortedMap):
    def subject(self, key):
        self.map()[key] = None

    @args(1)
    def test_different_key_types_raises(self):
        self.add_item("str-key")
        self.assertResultRaises(TypeError)


class TestKeysOrder(TestSortedMap):
    def subject(self):
        return [key for key in self.map().keys()]

    def test_sorted_order(self):
        self.add_item("t")
        self.add_item("a")
        self.add_item("d")
        self.assert_list(["a", "d", "t"])


class TestValuesOrder(TestSortedMap):
    def subject(self):
        return [value for value in self.map().values()]

    def test_sorted_key_order(self):
        self.add_item(5, "v1")
        self.add_item(3, "v2")
        self.add_item(10, "v3")
        self.assert_list(["v2", "v1", "v3"])


class TestItemsOrder(TestSortedMap):
    def subject(self):
        return [item for item in self.map().items()]

    def test_sorted_key_order(self):
        self.add_item(4, "v1")
        self.add_item(2, "v2")
        self.add_item(6, "v3")
        self.assert_list([(2, "v2"), (4, "v1"), (6, "v3")])
