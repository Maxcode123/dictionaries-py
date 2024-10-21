from unittest_extensions import args, TestCase

from maptypes.map import Map


def test_map_type(map_type: Map, namespace: dict):
    """
    Define all `Map` API tests for the given map type in the given namespace.

    Running `test_map_type(MapType, locals())` in a module is enough to run all
    tests for the `Map` protocol.
    """
    base_cls_name = "Test" + map_type.__name__
    namespace[base_cls_name] = _map_test_class(map_type)
    namespace[base_cls_name + "Iterator"] = _map_iterator_test_class(map_type)

    def create_test_map_class(suffix, base_test_class):
        namespace[base_cls_name + suffix] = type(
            base_cls_name + suffix,
            (namespace[base_cls_name], base_test_class),
            {},
        )

    def create_test_map_iterator_class(suffix, base_test_class):
        namespace[base_cls_name + suffix] = type(
            base_cls_name + suffix,
            (namespace[base_cls_name + "Iterator"], base_test_class),
            {},
        )

    create_test_map_class("SetItem", TestSetItem)
    create_test_map_class("GetItem", TestGetItem)
    create_test_map_class("DelItem", TestDelItem)
    create_test_map_class("Iter", TestIter)
    create_test_map_class("Len", TestLen)
    create_test_map_class("Eq", TestEq)
    create_test_map_class("Clear", TestClear)
    create_test_map_class("Get", TestGet)
    create_test_map_class("Items", TestItems)
    create_test_map_class("Keys", TestKeys)
    create_test_map_class("Values", TestValues)
    create_test_map_class("Pop", TestPop)
    create_test_map_class("PopDefault", TestPopDefault)
    create_test_map_iterator_class("ValuesIterator", TestValuesIterator)
    create_test_map_iterator_class("KeysIterator", TestKeysIterator)
    create_test_map_iterator_class("ItemsIterator", TestItemsIterator)


def _map_test_class(map_type: Map):
    """
    Create a base test class for a `Map` type.
    """
    cls_name = "Test" + map_type.__class__.__name__
    return type(cls_name, (TestMap, TestCase), dict(map_type=map_type))


def _map_iterator_test_class(map_type: Map):
    """
    Create a base test class for a `MapIterator` type.
    """
    cls_name = "Test" + map_type.__class__.__name__ + "Iterator"
    return type(cls_name, (TestMapIterator, TestCase), dict(map_type=map_type))


class TestMap:
    map_type: Map

    def setUp(self):
        self._map = self.map_type()

    def map(self):
        if self._map is None:
            self._map = self.map_type()

        return self._map

    def add_item(self, key, value):
        self.map().__setitem__(key, value)

    def assert_result_str(self, result_str, result_instance_check=False):
        if result_instance_check:
            self.assertResultIs(self.map())
        else:
            self.assertResultIsNot(self.map())
        self.assertSequenceEqual(str(self.cachedResult()), result_str, str)


class TestSetItem(TestMap):
    def subject(self, key, value):
        self.map()[key] = value
        return self.map()[key]

    @args(1, 2)
    def test_new_item(self):
        self.assertResult(2)

    @args({1}, 2)
    def test_unhashable_item_raises(self):
        self.assertResultRaisesRegex(TypeError, "unhashable type")

    @args("key", "new_value")
    def test_update_value(self):
        self.map()["key"] = "old_value"
        self.assertResult("new_value")


class TestGetItem(TestMap):
    def subject(self, key):
        return self.map()[key]

    @args(1)
    def test_new_key_raises(self):
        self.assertResultRaises(KeyError)

    @args({1})
    def test_unhashable_key_raises(self):
        self.assertResultRaisesRegex(TypeError, "unhashable type")

    @args("key")
    def test_gets_value(self):
        self.add_item("key", "value")
        self.assertResult("value")


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
        self.assertResultRaisesRegex(TypeError, "unhashable type")


class TestIter(TestMap):
    def subject(self):
        return [key for key in self.map()]

    def test_empty_map(self):
        self.assertEqual(len(self.result()), 0)

    def test_non_empty_map(self):
        self.add_item("key", "value")
        self.assertSequenceEqual(self.result(), ["key"], list)

    def test_does_not_mutate_keys(self):
        self.add_item("key", "value")
        for key in self.map():
            key = "new-key"
        self.assertEqual(self.map().__getitem__("key"), "value")


class TestLen(TestMap):
    def subject(self):
        return len(self.map())

    def test_empty_map(self):
        self.assertResult(0)

    def test_non_empty_map(self):
        self.add_item(1, 1)
        self.assertResult(1)


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


class TestClear(TestMap):
    def subject(self):
        self.map().clear()
        return self.map()

    def test_empty_map(self):
        self.assert_result_str("{}", result_instance_check=True)

    def test_non_empty_map(self):
        self.add_item(1, 1)
        self.assert_result_str("{}", result_instance_check=True)


class TestGet(TestMap):
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
        self.assertResultRaisesRegex(TypeError, "unhashable type")


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


class TestKeys(TestMap):
    def subject(self):
        return [k for k in self.map().keys()]

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
        self.assertResultRaisesRegex(TypeError, "unhashable type")


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


class TestMapIterator:
    map_type: Map

    def setUp(self):
        self._map = self.map_type()

    def map(self):
        if self._map is None:
            self._map = self.map_type()

        return self._map

    def add_item(self, key, value):
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
