from typing import Protocol, Self


class Map[KT, VT](Protocol):
    """
    A mutable map that associates keys with values.

    Keys need to be hashable.
    Values can be any object.
    """

    def __len__(self) -> int: ...

    def __iter__(self) -> "MapIterator[KT]": ...

    def __contains__(self, key: KT) -> bool: ...

    def __getitem__(self, key: KT) -> VT: ...

    def __setitem__(self, key: KT, value: VT) -> None: ...

    def __delitem__(self, key: KT) -> None: ...

    def __eq__(self, other) -> bool: ...

    def get[D](self, key: KT, default: D = None) -> VT | D:
        """
        Return the value for `key` if `key` is in the map, else `default`.
        If `default` is not given, it defaults to `None`, so that this method
        never raises `KeyError`.
        """

    def keys(self) -> "MapView[KT]":
        """
        Return a new view of the map's keys.
        """

    def values(self) -> "MapView[VT]":
        """
        Return a new view of the map's values.
        """

    def items(self) -> "MapView[tuple[KT, VT]]":
        """
        Return a new view of the map's items (`(key, value)` pairs).
        """

    __default = object()

    def pop[D](self, key: KT, default: D = __default) -> VT | D:
        """
        If `key` is in the map, remove it and return its value. If `key`
        is not found return `default` if given, else raise `KeyError`.
        """

    def clear(self) -> None:
        """
        Remove all items from the map.
        """


class MapIterator[T](Protocol):
    """
    Iterator of Map objects.
    """

    def __init__(self, _map: Map) -> None: ...

    def __iter__(self) -> Self: ...

    def __next__(self) -> T: ...


class MapView[T](Protocol):
    """
    View object of a Map.

    Provides a dynamic view of the map's entries; i.e. when the map changes,
    the view reflects these changes.
    """

    def __init__(self, _map: Map) -> None: ...

    def __iter__(self) -> MapIterator[T]: ...

    def __contains__(self, x: T) -> bool: ...

    def __len__(self) -> int: ...
