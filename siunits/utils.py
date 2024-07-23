from _collections_abc import dict_items
from typing import TypeVar, Any
from functools import wraps, reduce
from sortedcontainers import SortedDict, SortedItemsView  # type: ignore

SMALL_SPACE = "\u2009"
MULTIPLY_SIGN = "\u22C5"

T = TypeVar("T")
U = TypeVar("U")

def product(iterable, initial=1):
    return reduce(lambda x, y: x * y, iterable, initial)

class DefaultSortedDict(SortedDict[T, U]):
    def __init__(self, default_factory=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __missing__(self, key: T):
        self[key] = value = self.default_factory() if self.default_factory is not None else None
        return value

def commutative(cls):
    # 오버로딩된 이항 연산자들을 정의
    binary_operators = [
        '__add__', '__sub__', '__mul__', '__matmul__', '__truediv__', '__floordiv__',
        '__mod__', '__divmod__', '__pow__', '__lshift__', '__rshift__', '__and__',
        '__xor__', '__or__'
    ]

    # 각 연산자에 대해 역-연산자 설정
    for op in binary_operators:
        reverse_op = '__r' + op[2:]  # '__add__' -> '__radd__' 변환
        if hasattr(cls, op):
            original_method = getattr(cls, op)

            @wraps(original_method)
            def method(self, other):
                return original_method(other, self)

            setattr(cls, reverse_op, method)

    return cls

K = TypeVar("K")

@commutative
class ArithmeticDict(DefaultSortedDict[K, int | float]):
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

    def __deepcopy__(self, memodict={}):
        return ArithmeticDict(self)

    def items(self) -> 'dict_items[K, int | float]':
        return super().items()

class Multitone(type):
    _instances: dict[tuple, 'Multitone'] = {}

    def __call__(cls, *args, **kwargs):
        kwargs_key = tuple(sorted(kwargs.items()))
        key = (cls, *args, kwargs_key)

        if key not in cls._instances:
            cls._instances[key] = super().__call__(*args, **kwargs)
        return cls._instances[key]

def pretty(n: int | float, precision: int = 2) -> str:
    return f"{n:.0f}" if float(n).is_integer() else f"{n:.{precision}f}"
