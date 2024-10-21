from abc import abstractmethod, ABC
from typing import Self


def _key_typecheck(key) -> None:
    # Prefer `hasattr` over decorating a KeyType protocol with
    # @runtime_checkable and checking with `isinstance`.
    # The latter can be surprisingly slow.
    # https://docs.python.org/3/library/typing.html#typing.runtime_checkable
    if not hasattr(key, "__lt__") or getattr(key, "__lt__") is None:
        raise TypeError(f"uncomparable type: '{type(key).__name__}'")

    hash(key)  # will raise TypeError if unhashable


class BSMap:
    """
    Sorted binary-search map.

    Supports keys that are comparable and hashable.
    In any instance the keys must be comparable to each other, i.e. integers
    and strings cannot be used as keys in the same instance.
    """

    __default = object()

    def __init__(self):
        self._keys = list()
        self._values = list()

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> "BSMapKeysIterator":
        return BSMapKeysIterator(self)

    def __contains__(self, key) -> bool:
        _key_typecheck(key)

        i = self._rank(key)

        if i < len(self) and self._keys[i] == key:
            return True

        return False

    def __getitem__(self, key):
        _key_typecheck(key)

        i = self._rank(key)

        if i < len(self) and self._keys[i] == key:
            return self._values[i]

        raise KeyError(key)

    def __setitem__(self, key, value) -> None:
        _key_typecheck(key)

        i = self._rank(key)
        size = len(self)

        if i < size and self._keys[i] == key:
            self._values[i] = value
            return

        if size > 0:
            self._keys.insert(i, key)
            self._values.insert(i, value)
        else:
            self._keys.append(key)
            self._values.append(value)

    def __delitem__(self, key) -> None:
        _key_typecheck(key)

        i = self._rank(key)

        if i < len(self) and self._keys[i] == key:
            self._keys.pop(i)
            self._values.pop(i)
            return

        raise KeyError(key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, (dict, BSMap)):
            return False

        if len(self) != len(other):
            return False

        for i, key in enumerate(self._keys):
            if self._values[i] != other[key]:
                return False

        return True

    def __repr__(self) -> str:
        return "<BSMap<" + str(self) + ">"

    def __str__(self) -> str:
        if len(self._keys) == 0:
            return "{}"

        nodes_str = []
        for key, value in zip(self._keys, self._values):
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

    def keys(self) -> "BSMapKeysView":
        return BSMapKeysView(self)

    def values(self) -> "BSMapValuesView":
        return BSMapValuesView(self)

    def items(self) -> "BSMapItemsView":
        return BSMapItemsView(self)

    def pop(self, key, default=__default):
        """
        If `key` is in the map, remove it and return its value. If not, return
        `default` if it is given, else raise `KeyError`.
        """
        _key_typecheck(key)

        i = self._rank(key)

        if i < len(self) and self._keys[i] == key:
            self._keys.pop(i)
            return self._values.pop(i)

        if default is not self.__default:  # a default value has been given
            return default

        raise KeyError(key)

    def clear(self) -> None:
        """
        Clears all items from the map.
        """
        self._keys.clear()
        self._values.clear()

    def _rank(self, key) -> int:
        """
        Return the index of the key in the arrays.
        Return 0 if the given key is smaller than the smallest key.
        Return len(self) if the given key is bigger than the biggest key.
        """
        low = 0
        high = len(self) - 1

        while low <= high:
            mid = low + (high - low) // 2
            mid_key = self._keys[mid]

            if key < mid_key:
                high = mid - 1
            elif mid_key < key:
                low = mid + 1
            else:  # key == mid_key
                return mid

        return low


class BSMapIterator(ABC):
    """
    Abstract base class for iterators operating on `BSMap`.
    """

    def __iter__(self) -> Self:
        return self

    def __next__(self):
        self._current_index += 1

        if self._current_index == self._len():
            raise StopIteration

        return self._iterator_item()

    @abstractmethod
    def _iterator_item(self):
        raise NotImplementedError

    @abstractmethod
    def _len(self) -> int:
        raise NotImplementedError


class BSMapKeysIterator(BSMapIterator):
    def __init__(self, _map: BSMap) -> None:
        self._keys = _map._keys
        self._current_index = -1

    def _iterator_item(self):
        return self._keys[self._current_index]

    def _len(self) -> int:
        return len(self._keys)


class BSMapValuesIterator(BSMapIterator):
    def __init__(self, _map: BSMap) -> None:
        self._values = _map._values
        self._current_index = -1

    def _iterator_item(self):
        return self._values[self._current_index]

    def _len(self) -> int:
        return len(self._values)


class BSMapItemsIterator(BSMapIterator):
    def __init__(self, _map: BSMap) -> None:
        self._keys = _map._keys
        self._values = _map._values
        self._current_index = -1

    def _iterator_item(self) -> tuple:
        return (
            self._keys[self._current_index],
            self._values[self._current_index],
        )

    def _len(self) -> int:
        return len(self._keys)


class BSMapView(ABC):
    """
    Abstract base class for views of `BSMap` objects.
    """

    _iterator: BSMapIterator

    def __iter__(self) -> BSMapIterator:
        return self._iterator(self._map)


class BSMapKeysView(BSMapView):
    _iterator = BSMapKeysIterator

    def __init__(self, _map: BSMap) -> None:
        self._map = _map
        self._keys = _map._keys

    def __len__(self) -> int:
        return len(self._keys)

    def __contains__(self, key) -> bool:
        _key_typecheck(key)

        i = self._map._rank(key)

        if i < len(self) and self._keys[i] == key:
            return True

        return False


class BSMapValuesView(BSMapView):
    _iterator = BSMapValuesIterator

    def __init__(self, _map: BSMap) -> None:
        self._map = _map
        self._values = _map._values

    def __len__(self) -> int:
        return len(self._values)

    def __contains__(self, value) -> bool:
        return value in self._values


class BSMapItemsView(BSMapView):
    _iterator = BSMapItemsIterator

    def __init__(self, _map: BSMap) -> None:
        self._map = _map
        self._keys = _map.keys
        self._values = _map._values

    def __len__(self) -> int:
        return self(self._keys)

    def __contains__(self, item) -> bool:
        if not isinstance(item, tuple):
            return False

        if not len(item) == 2:
            return False

        key, value = item

        _key_typecheck(key)

        i = self._map._rank(key)

        if i < len(self._keys) and self._keys[i] == key:
            return self._values[i] == value
