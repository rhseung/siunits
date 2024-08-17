import numpy as np
from numpy.typing import ArrayLike, NDArray
from plum import dispatch

from siunits.predefined import kg, m, atm
from siunits.types import UnitBase, ComplexUnit
from siunits.dimension import Dimension, DimensionError, dimensionless

from typing import Any, Self, Literal, TypeAlias, Union, Any, overload
from functools import total_ordering
from numbers import Number as PyNumber
from fractions import Fraction
from decimal import Decimal
from copy import deepcopy

__all__ = ["Quantity"]

QuantityLike: TypeAlias = Union['Quantity', UnitBase]
Number: TypeAlias = Union[Decimal, Fraction, PyNumber, np.number]

@total_ordering
class Quantity(np.ndarray):
    # create instance
    def __new__(cls: type['Quantity'], value: ArrayLike, unit: UnitBase) -> 'Quantity':
        _multiplier = unit.multiplier
        unit.multiplier = 1

        obj = (np.asarray(value) * _multiplier).view(cls)
        obj._unit = unit

        return obj
    def __array_finalize__(self: Self, obj: NDArray[Any] | None) -> None:
        if obj is None:
            return

        _unit = getattr(obj, "_unit", None)
        if _unit is not None:
            self._unit = _unit

    # properties
    @property
    def unit(self: Self) -> UnitBase:
        return self._unit
    @unit.setter
    def unit(self: Self, unit: UnitBase) -> None:
        if not self.unit.dimension == unit.dimension:
            raise DimensionError(self.unit.dimension, unit.dimension, "Cannot change unit to different dimension")

        self._unit = unit
    @property
    def value(self: Self) -> NDArray[Any]:
        return self.view(np.ndarray)
    @value.setter
    def value(self: Self, value: ArrayLike) -> None:
        self[...] = value

    # private methods
    def _to_complex_unit(self: Self) -> ComplexUnit:
        _cp = self.unit ** 1
        _cp.multiplier = self.value
        return _cp
    def _repr_latex_(self: Self) -> str:
        return self.to_string(format="latex")

    # public methods
    @overload
    def to_string(self: Self, *, format: Literal['latex'], precision: int | None = None) -> str:
        return self._to_complex_unit()._repr_latex_()
    @overload
    def to_string(self: Self, *, format: None = None, precision: int | None = None) -> str:
        return self._to_complex_unit().__str__()
    @dispatch
    def to_string(self, *, format, precision):
        return NotImplemented
    
    def decompose(self: Self) -> 'Quantity':
        _cp = self._to_complex_unit().expand()
        return Quantity(1, _cp)
    def compose(self: Self) -> list['Quantity']:
        # TODO: implement
        return []
    def si(self: Self) -> 'Quantity':
        _cp = self._to_complex_unit().si()
        return Quantity(1, _cp)
    
    @overload
    def to(self: Self, unit: UnitBase) -> 'Quantity':
        if self.unit.dimension != unit.dimension:
            raise DimensionError(self.unit.dimension, unit.dimension, "Cannot convert between different dimensions")

        return Quantity(1, self._to_complex_unit().to(unit))
    @overload
    def to(self: Self, unit: 'Quantity') -> 'Quantity':
        if self.unit.dimension != unit.unit.dimension:
            raise DimensionError(self.unit.dimension, unit.unit.dimension, "Cannot convert between different dimensions")

        return Quantity(1, self._to_complex_unit().to(unit._to_complex_unit()))
    @dispatch
    def to(self, unit):
        return NotImplemented

    # magic methods
    def __str__(self: Self) -> str:
        return self.to_string()
    def __repr__(self: Self) -> str:
        return f"<{self.__class__.__name__} {self.value} {self.unit}>"
    def __format__(self: Self, format_spec: str) -> str:
        if format_spec == "":
            return self.to_string()
        elif format_spec == 'latex':
            return self.to_string(format='latex')
        else:
            return f"{format(self.value, format_spec)} {self.unit}"
    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        return Quantity(deepcopy(self.value), deepcopy(self.unit))
    def __contains__(self, item):
        return NotImplemented

    # conversion operators
    @overload
    def __lshift__(self: Self, other: UnitBase) -> 'Quantity':
        return self.to(other)
    @overload
    def __lshift__(self, other: 'Quantity') -> 'Quantity':
        return self.to(other._to_complex_unit())
    @dispatch
    def __lshift__(self, other):
        return NotImplemented
    
    def __rshift__(self, other):
        return NotImplemented

    # unary operators
    def __pos__(self) -> Self:
        return self
    def __neg__(self) -> 'Quantity':
        return Quantity(-self.value, self.unit)
    def __abs__(self) -> 'Quantity':
        return Quantity(abs(self.value), self.unit)

    # arithmetic operators
    def __eq__(self, other: QuantityLike) -> NDArray[np.bool]:
        other <<= self
        return self.value.__eq__(other.value)
    def __lt__(self, other: QuantityLike) -> NDArray[np.bool]:
        other <<= self
        return self.value.__lt__(other.value)

if __name__ == "__main__":
    q = Quantity([1, 2, 3], atm.expand())
    q2 = Quantity([2, 3, 4], kg)
    q.value = np.array([2, 3, 4])
    print(q)

