from typing import Self
from abc import ABC, abstractmethod


def _key_typecheck(key) -> None:
    # Prefer `hasattr` over decorating a KeyType protocol with
    # @runtime_checkable and checking with `isinstance`.
    # The latter can be surprisingly slow.
    # https://docs.python.org/3/library/typing.html#typing.runtime_checkable
    if not hasattr(key, "__lt__") or getattr(key, "__lt__") is None:
        raise TypeError(f"uncomparable type: '{type(key).__name__}'")

    hash(key)  # will raise TypeError if unhashable


class Node:
    def __init__(self, key, value, size) -> None:
        self.key = key
        self.value = value
        self.size = size
        self.left = None
        self.right = None

    def resize(self) -> None:
        """
        Re-calculate node size from size of subtrees.
        """
        self.size = self._size(self.left) + self._size(self.right) + 1

    def to_item(self) -> tuple:
        """
        Return the `(key, value)` pair of this node.
        """
        return (self.key, self.value)

    @staticmethod
    def _size(node) -> int:
        return node.size if node is not None else 0


class BSTMap:
    """
    Sorted binary-search-tree map.

    Supports keys that are comparable and hashable.
    In any instance the keys must be comparable to each other, i.e. integers
    and strings cannot be used as keys in the same instance.
    """

    __default = object()

    def __init__(self) -> None:
        self._root = None

    def __len__(self) -> int:
        return self._root.size if self._root is not None else 0

    def __iter__(self) -> "BSTMapKeysIterator":
        return BSTMapKeysIterator(self)

    def __contains__(self, key) -> bool:
        _key_typecheck(key)

        return key in self.keys()

    def __getitem__(self, key):
        _key_typecheck(key)

        value = self._get(self._root, key)

        if value is self.__default:
            raise KeyError(key)

        return value

    def __setitem__(self, key, value) -> None:
        _key_typecheck(key)

        self._root = self._set(self._root, key, value)

    def __delitem__(self, key) -> None:
        _key_typecheck(key)

        self._root = self._delete(self._root, key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, (dict, BSTMap)):
            return False

        if len(self) != len(other):
            return False

        for key, value in self.items():
            if value != other[key]:
                return False

        return True

    def __repr__(self) -> str:
        return "<BSTMap<" + str(self) + ">"

    def __str__(self) -> str:
        if len(self) == 0:
            return "{}"

        nodes_str = []
        for key, value in self.items():
            v = "{...}" if value is self else str(value)
            nodes_str.append(f"{key}: " + v + ", ")

        nodes_str[-1] = nodes_str[-1].rstrip(", ")

        return "{" + "".join(nodes_str) + "}"

    def get(self, key, default=None):
        """
        Return the value for `key` if `key` is in the map, else `default`
        If `default` is not given, it defaults to `None`, so that this method
        never raises `KeyError`.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> "BSTMapKeysView":
        return BSTMapKeysView(self)

    def values(self) -> "BSTMapValuesView":
        return BSTMapValuesView(self)

    def items(self) -> "BSTMapItemsView":
        return BSTMapItemsView(self)

    def pop(self, key, default=__default):
        """
        If `key` is in the map, remove it and return its value. If not, return
        `default` if it is given, else raise `KeyError`.
        """
        _key_typecheck(key)

        self._root, node = self._pop(self._root, key)

        if node is not None:
            return node.value

        if default is not self.__default:  # a default value has been given
            return default

        raise KeyError(key)

    def clear(self) -> None:
        """
        Clears all items from the map.
        """
        self._root = None

    def _get(self, node, key):
        """
        Get the value associated with `key` from the tree rooted at the given
        node. Return __default if the value is not found.

        `key` is expected to be typechecked.
        """
        if node is None:
            return self.__default

        if key < node.key:
            return self._get(node.left, key)
        elif node.key < key:
            return self._get(node.right, key)
        else:  # key == node.key
            return node.value

    def _set(self, node, key, value):
        """
        Associate `key` with `value` in the tree rooted at the given node
        and return the node that will hold `key`.

        `key` is expected to be typechecked.
        """
        if node is None:
            return Node(key, value, 1)

        if key < node.key:
            node.left = self._set(node.left, key, value)
        elif node.key < key:
            node.right = self._set(node.right, key, value)
        else:  # key == node.key
            node.value = value

        node.resize()

        return node

    def _delete(self, node, key):
        """
        Delete the entry associated with `key` from the tree rooted at the given
        node.

        `key` is expected to be typechecked.
        """
        if node is None:
            raise KeyError(key)

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif node.key < key:
            node.right = self._delete(node.right, key)
        else:  # key == node.key
            if node.right is None:
                return node.left

            if node.left is None:
                return node.right

            # Eager Hibbard BST deletion algorithm
            # 1. Save a link to the node to be deleted
            tmp = node
            # 2. Set node to point to its successor
            node = self._get_min(tmp.right)
            # 3. Set the right link of node to point to the BST
            # containing all keys larger than itself
            node.right = self._delete_min(tmp.right)
            # 4. Set the left link of node to point to the BST
            # containing all keys smaller than itself
            node.left = tmp.left

        node.resize()

        return node

    def _get_min(self, node):
        """
        Get the smallest node from the tree rooted at the given node.
        """
        return node if node.left is None else self._get_min(node.left)

    def _delete_min(self, node):
        """
        Delete the smallest node for the tree rooted at the given node
        and return the node that substitutes the given one.
        """
        if node.left is None:
            return node.right

        node.left = self._delete_min(node.left)

        node.resize()

        return node

    def _pop(self, node, key):
        """
        Delete the entry associated with `key` from the tree rooted at the
        given node and return the new root and the deleted node.
        Return root, None if the key is not found.

        `key` is expected to be typechecked.
        """
        if node is None:
            return node, None

        if key < node.key:
            node.left, deleted = self._pop(node.left, key)
        elif node.key < key:
            node.right, deleted = self._pop(node.right, key)
        else:  # key == node.key
            if node.right is None:
                return node.left, node

            if node.left is None:
                return node.right, node

            deleted = node
            node = self._get_min(deleted.right)
            node.right = self._delete_min(deleted.right)
            node.left = deleted.left

        node.resize()

        return node, deleted


class BSTMapIterator(ABC):
    """
    Abstract base class for iterators operating on `BSTMap`.
    """

    def __init__(self, _map: BSTMap) -> None:
        self._map = _map
        self._current_index = -1
        self._nodes = list()
        self._append_nodes(_map._root, self._nodes)

    def __iter__(self) -> Self:
        return self

    def __next__(self):
        self._current_index += 1

        if self._current_index == self._len():
            raise StopIteration

        return self._iterator_item()

    def _len(self) -> int:
        return len(self._map)

    def _append_nodes(self, node, node_list) -> None:
        if node is None:
            return

        if node.left is not None:
            self._append_nodes(node.left, node_list)

        node_list.append(node)

        if node.right is not None:
            self._append_nodes(node.right, node_list)

    @abstractmethod
    def _iterator_item(self):
        raise NotImplementedError


class BSTMapKeysIterator(BSTMapIterator):
    def _iterator_item(self):
        return self._nodes[self._current_index].key


class BSTMapValuesIterator(BSTMapIterator):
    def _iterator_item(self):
        return self._nodes[self._current_index].value


class BSTMapItemsIterator(BSTMapIterator):
    def _iterator_item(self):
        return self._nodes[self._current_index].to_item()


class BSTMapView(ABC):
    """
    Abstract base class for views of `BSTMap` objects.
    """

    _iterator: BSTMapIterator

    def __iter__(self) -> BSTMapIterator:
        return self._iterator(self._map)


class BSTMapKeysView(BSTMapView):
    _iterator = BSTMapKeysIterator

    __default = object()

    def __init__(self, _map: BSTMap) -> None:
        self._map = _map

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, key) -> bool:
        _key_typecheck(key)

        if self._map.get(key, self.__default) is self.__default:
            return False

        return True


class BSTMapValuesView(BSTMapView):
    _iterator = BSTMapValuesIterator

    def __init__(self, _map: BSTMap) -> None:
        self._map = _map

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, value) -> bool:
        return value in map(lambda n: n.value, iter(self))


class BSTMapItemsView(BSTMapView):
    _iterator = BSTMapItemsIterator

    def __init__(self, _map: BSTMap) -> None:
        self._map = _map

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, item) -> bool:
        if not isinstance(item, tuple):
            return False

        if not len(item) == 2:
            return False

        key, value = item

        _key_typecheck(key)

        if self._map._get(self._map._root, key) == value:
            return True

        return False
