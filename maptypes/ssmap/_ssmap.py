from typing import Self
from abc import abstractmethod, ABC


class Node[KT, VT]:
    """
    Node of the list used for the implementation of `SSMap`.
    """

    def __init__(self, key: KT, value: VT, key_hash: int) -> None:
        self.key_hash = key_hash
        self.key = key
        self.value = value

    def to_item(self) -> tuple[KT, VT]:
        return (self.key, self.value)


class SSMap[KT, VT]:
    """
    Sequential-search map.
    """

    def __init__(self):
        self._list = list()

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> "SSMapKeysIterator[KT]":
        return SSMapKeysIterator(self)

    def __contains__(self, key: KT) -> bool:
        return key in self.keys()

    def __getitem__(self, key: KT) -> VT:
        key_hash = hash(key)

        for node in self._list:
            if node.key_hash == key_hash:
                return node.value

        raise KeyError(key)

    def __setitem__(self, key: KT, value: VT) -> None:
        key_hash = hash(key)

        for node in self._list:
            if node.key_hash == key_hash:
                node.value = value
                return

        self._list.append(Node(key, value, key_hash))

    def __delitem__(self, key: VT) -> None:
        key_hash = hash(key)

        for i, node in enumerate(self._list):
            if node.key_hash == key_hash:
                self._list.pop(i)
                return

        raise KeyError(key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, (dict, SSMap)):
            return False

        if len(other) != len(self):
            return False

        for key, value in other.items():
            if self[key] != value:
                return False

        return True

    def __repr__(self):
        return "SSMap<" + str(self) + ">"

    def __str__(self):
        if len(self._list) == 0:
            return "{}"

        nodes_str = []
        for node in self._list:
            value = "{...}" if node.value is self else str(node.value)
            nodes_str.append(f"{node.key}: " + value + ", ")

        nodes_str[-1] = nodes_str[-1].rstrip(", ")

        return "{" + "".join(nodes_str) + "}"

    def get[D](self, key: KT, default: D = None) -> VT | D:
        """
        Return the value for `key` if `key` is in the map, else `default`
        If `default` is not given, it defaults to `None`, so that this method
        never raises `KeyError`.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> "SSMapKeysView":
        """
        Return a new view of the map's keys.
        """
        return SSMapKeysView(self)

    def values(self) -> "SSMapValuesView":
        """
        Return a new view of the map's values.
        """
        return SSMapValuesView(self)

    def items(self) -> "SSMapItemsView":
        """
        Return a new view of the map's items (`(key, value)` pairs).
        """
        return SSMapItemsView(self)

    __default = object()

    def pop[D](self, key: KT, default: D = __default) -> VT | D:
        """
        If `key` is in the map, remove it and return its value. If not, return
        `default` if it is given, else raise `KeyError`.
        """
        key_hash = hash(key)

        for i, node in enumerate(self._list):
            if node.key_hash == key_hash:
                return self._list.pop(i).value

        if default is not self.__default:  # a default value has been given
            return default

        raise KeyError(key)

    def clear(self) -> None:
        """
        Clears all items from the map.
        """
        self._list.clear()


class SSMapIterator[T](ABC):
    """
    Abstract base class for iterators operating on `SSMap`.
    """

    def __init__(self, _dict: SSMap) -> None:
        self._list = _dict._list
        self._current_index = -1
        self._len = len(self._list)

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> T:
        self._current_index += 1

        if self._current_index == self._len:
            raise StopIteration

        return self._iterator_item()

    @abstractmethod
    def _iterator_item(self) -> T:
        raise NotImplementedError


class SSMapKeysIterator[KT](SSMapIterator):
    def _iterator_item(self) -> KT:
        return self._list[self._current_index].key


class SSMapValuesIterator[VT](SSMapIterator):
    def _iterator_item(self) -> VT:
        return self._list[self._current_index].value


class SSMapItemsIterator[KT, VT](SSMapIterator):
    def _iterator_item(self) -> tuple[KT, VT]:
        return self._list[self._current_index].to_item()


class SSMapView(ABC):
    """
    Abstract base class for views of `SSMap` objects.
    """

    _iterator: SSMapIterator

    def __init__(self, _dict: SSMap) -> None:
        self._dict = _dict
        self._list = _dict._list

    def __iter__(self) -> SSMapIterator:
        return self._iterator(self._dict)

    def __len__(self) -> int:
        return len(self._list)


class SSMapKeysView(SSMapView):
    _iterator = SSMapKeysIterator

    def __contains__(self, key) -> bool:
        key_hash = hash(key)

        for node in self._list:
            if node.key_hash == key_hash:
                return True

        return False


class SSMapValuesView(SSMapView):
    _iterator = SSMapValuesIterator

    def __contains__(self, value) -> bool:
        for node in self._list:
            if node.value == value:
                return True

        return False


class SSMapItemsView(SSMapView):
    _iterator = SSMapItemsIterator

    def __contains__(self, item) -> bool:
        for node in self._list:
            if (node.key, node.value) == item:
                return True

        return False
