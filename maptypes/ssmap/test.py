from maptypes.ssmap import SSMap
from maptypes._test import test_map_type

test_map_type(SSMap, locals())


class TestSSMapIterOrder(TestSSMap):
    def subject(self):
        return [key for key in self.map()]

    def test_fifo_order(self):
        self.add_item(3, None)
        self.add_item(2, None)
        self.add_item(5, None)
        self.assertSequenceEqual(self.result(), [3, 2, 5], list)


class TestSSMapSetItemDifferentOrder(TestSSMap):
    def test_different_types_dont_raise(self):
        self.add_item(1)
        self.add_item("something")


class TestSSMapKeysOrder(TestSSMap):
    def subject(self):
        return [key for key in self.map().keys()]

    def test_fifo_order(self):
        self.add_item(3)
        self.add_item(2)
        self.add_item(5)
        self.assertSequenceEqual(self.result(), [3, 2, 5], list)


class TestSSMapValuesOrder(TestSSMap):
    def subject(self):
        return [value for value in self.map().values()]

    def test_fifo_order(self):
        self.add_item(3, "v1")
        self.add_item(2, "v2")
        self.add_item(5, "v3")
        self.assertSequenceEqual(self.result(), ["v1", "v2", "v3"], list)
