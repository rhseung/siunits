import numpy as np
from attrs import define

from typing import overload, Callable
from math import log

@define
class Measure:
    converter: Callable[[float], float] = lambda x: x

    def __call__(self, x: float) -> float:
        return self.converter(x)

    def __pos__(self) -> 'Measure':
        return self

    def __neg__(self) -> 'Measure':
        return Measure(lambda x: -self.converter(x))

    def __add__(self, other) -> 'Measure':
        if isinstance(other, (int, float)):
            return Measure(lambda x: self.converter(x) + other)
        elif isinstance(other, Measure):
            return Measure(lambda x: self.converter(x) + other.converter(x))
        else:
            return NotImplemented

    def __radd__(self, other) -> 'Measure':
        return self.__add__(other)

    def __sub__(self, other: 'Measure | int | float') -> 'Measure':
        return self.__add__(-other)

    def __rsub__(self, other: 'Measure | int | float') -> 'Measure':
        return (-self).__add__(other)

    def __mul__(self, other: int | float) -> 'Measure':
        return Measure(lambda x: self.converter(x) * other)

    def __rmul__(self, other: int | float) -> 'Measure':
        return self.__mul__(other)

    def __truediv__(self, other: int | float) -> 'Measure':
        return Measure(lambda x: self.converter(x) / other)

    def __rtruediv__(self, other: int | float) -> 'Measure':
        return Measure(lambda x: other / self.converter(x))

    def __pow__(self, power: int | float) -> 'Measure':
        return Measure(lambda x: self.converter(x) ** power)

    def __rpow__(self, base: int | float) -> 'Measure':
        return Measure(lambda x: base ** self.converter(x))

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs) -> 'Measure':
        return Measure(lambda x: ufunc(self.converter(x), *inputs[1:], **kwargs))

if __name__ == '__main__':
    C = Measure()
    K = C + 273.15
    F = 9/5 * C + 32
    dB = 10 * np.log10(C)
    pH = -np.log10(C)
    custom = np.exp(C) + 1
    
    print(C(100))
    print(K(100))  # 373.15
    print(F(100))  # 212.0
    print(dB(100))  # 20.0
    print(pH(4.5e-4))  # ~ 3.35
    print(custom(1))  # ~ 3.71828
