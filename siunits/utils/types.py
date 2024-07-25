from _collections_abc import dict_items, dict_keys, dict_values
from sortedcontainers import SortedDict, SortedItemsView, SortedKeysView, SortedValuesView
from .functions import commutative

class DefaultSortedDict[T, U](SortedDict[T, U]):
    def __init__(self, default_factory=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __missing__(self, key: T):
        self[key] = value = self.default_factory() if self.default_factory is not None else None
        return value

@commutative
class ArithmeticDict[K](DefaultSortedDict[K, int | float]):
    def __init__(self, *args, **kwargs):
        super().__init__(int, *args, **kwargs)

    def __add__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] + other[k] for k in (self.keys() | other.keys())})

    def __sub__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] - other[k] for k in (self.keys() | other.keys())})

    def __mul__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] * other[k] for k in (self.keys() | other.keys())})

    def __truediv__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] / other[k] for k in (self.keys() | other.keys())})

    def __floordiv__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] // other[k] for k in (self.keys() | other.keys())})

    def __mod__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] % other[k] for k in (self.keys() | other.keys())})

    def __pow__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] ** other[k] for k in (self.keys() | other.keys())})

    def __or__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        d = {}
        for k in (self.keys() | other.keys()):
            if k in self:
                d[k] = self[k]
            elif k in other:
                d[k] = other[k]

        return ArithmeticDict(d)

    def __and__(self, other: 'ArithmeticDict[K]') -> 'ArithmeticDict[K]':
        d = {}
        for k in (self.keys() | other.keys()):
            if k in self and k in other:
                d[k] = self[k]

        return ArithmeticDict(d)

    def __neg__(self) -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: -self[k] for k in self.keys()})

    def __pos__(self) -> 'ArithmeticDict[K]':
        return self

    def __abs__(self) -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: abs(self[k]) for k in self.keys()})

    def __round__(self, n: int = 0) -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: round(self[k], n) for k in self.keys()})

    def __floor__(self) -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] // 1 for k in self.keys()})

    def __ceil__(self) -> 'ArithmeticDict[K]':
        return ArithmeticDict({k: self[k] // 1 + 1 for k in self.keys()})

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}

        return ArithmeticDict(self)

    def items(self) -> 'dict_items[K, int | float]':
        return super().items()

    def keys(self) -> 'dict_keys[K, int | float]':
        return super().keys()

    def values(self) -> 'dict_values[K, int | float]':
        return super().values()

# class Multitone(type):
#     _instances: dict[tuple, 'Multitone'] = {}
#
#     def __call__(cls, *args, **kwargs):
#         key = (cls, kwargs.get('tone', None))
#
#         if key not in cls._instances:
#             cls._instances[key] = super().__call__(*args, **kwargs)
#
#         return cls._instances[key]

# class A[**T]:
#     def __init__(self):
#         self.data = T.

__all__ = ['DefaultSortedDict', 'ArithmeticDict']
