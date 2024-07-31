import re
from abc import abstractmethod
from copy import deepcopy
from typing import TypeVar, overload
from functools import total_ordering

from plum import dispatch
from attrs import define
from numpy import ndarray, array

from siunits.utils import (
    ArithmeticDict, product, pretty,
    SMALL_SPACE, MULTIPLY_SIGN, SMALL_SPACE_LATEX, MULTIPLY_SIGN_LATEX
)
from siunits.dimension import Dimension, DimensionError, dimensionless

Number = int | float
ArrayLike = list[Number] | tuple[Number, ...] | ndarray | range

# %% UnitBase

class UnitBase:
    def __init__(self, dimension: Dimension, offset: Number = 0, multiplier: Number = 1, depth: int = 0):
        self.dimension = dimension
        self.offset = offset
        self._multiplier = multiplier
        self.depth = depth

    @property
    def multiplier(self):
        return self._multiplier

    @multiplier.setter
    def multiplier(self, value: Number):
        if isinstance(value, float) and value.is_integer():
            value = int(value)

        self._multiplier = value

    def __eq__(self, other):
        return _eq(self, other)

    def __add__(self, other: 'UnitBase | Quantity'):
        return _add(self, other)

    def __radd__(self, other: 'UnitBase | Quantity'):
        return _add(self, other)

    def __sub__(self, other: 'UnitBase | Quantity'):
        # return self.__add__(-other)
        return _sub(self, other)

    def __rsub__(self, other: 'UnitBase | Quantity'):
        return -_sub(self, other)
        # return -self.__sub__(other)

    def __mul__(self, other: 'UnitBase | Quantity | Number | ArrayLike'):
        return _mul(self, other)

    def __rmul__(self, other: 'UnitBase | Quantity | Number | ArrayLike'):
        return _mul(self, other)

    def __truediv__(self, other: 'UnitBase | Quantity | Number | ArrayLike'):
        return _div(self, other)

    def __rtruediv__(self, other: 'UnitBase | Quantity | Number | ArrayLike'):
        # return 1 / self.__truediv__(other)
        return _div(other, self)

    def __pow__(self, exponent: Number):
        return _pow(self, exponent)

    def __pos__(self):
        return self

    def __neg__(self):
        return self * -1

    # todo: multiplier에 complex 지원
    #  - __complex__

    def __repr__(self) -> str:
        ret = f"<{self.__class__.__name__}[{self.dimension}]>"
        if self.offset != 0:
            ret += f" offset={self.offset}"
        if self.multiplier != 1:
            ret += f" multiplier={self.multiplier}"
        return ret

    def __str__(self) -> str:
        return self.__format__("")

    @abstractmethod
    def __contains__(self, unit: 'UnitBase') -> bool:
        pass

    @abstractmethod
    def __deepcopy__(self, memo=None):
        pass

    @abstractmethod
    def __format__(self, format_spec: str) -> str:
        pass

    @abstractmethod
    def _repr_latex_(self) -> str:
        pass

    @abstractmethod
    def expand(self):
        pass

    @abstractmethod
    def si(self):
        pass

    # test: 테스트 필요
    def to(self, other: 'UnitBase') -> 'UnitBase':
        if self.dimension != other.dimension:
            raise DimensionError(self.dimension, other.dimension, "Cannot convert units with different dimensions")

        ret = deepcopy(other**1)
        ret.multiplier = self.si().multiplier / other.si().multiplier
        return ret

U = TypeVar('U', bound=UnitBase)

# %% Unit
class Unit(UnitBase):
    _instances: dict[tuple, 'Unit'] = {}

    def __new__(cls, symbol: str, dimension: Dimension, offset: Number = 0, multiplier: Number = 1, *args,
                **kwargs):
        key = (cls, symbol, dimension, offset, multiplier)

        # if len(cls._instances) > 7:
        #     raise ValueError("SI units should be defined only once")

        if key not in cls._instances:
            cls._instances[key] = super().__new__(cls)

        return cls._instances[key]

    def __init__(self, symbol: str, dimension: Dimension, offset: Number = 0, multiplier: Number = 1, *, latex_symbol: str | None = None):
        super().__init__(dimension, offset, multiplier)
        self.symbol = symbol
        self.latex_symbol = symbol if latex_symbol is None else latex_symbol

    def __hash__(self) -> int:  # type: ignore
        if self.multiplier == 0:    # todo: offset, 0K, 0C의 경우처럼 0이여도 다른 경우가 있을 수 있음
            return hash(0)
        elif self.dimension == dimensionless:
            return hash(self.multiplier)
        else:
            return hash((self.symbol, self.dimension, self.offset, self.multiplier))

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        return Unit(self.symbol, self.dimension, self.offset, self.multiplier, latex_symbol=self.latex_symbol)

    def __lt__(self, other) -> bool:
        if not isinstance(other, Unit):
            return NotImplemented

        a, b = self.symbol, other.symbol

        # 배수가 큰 것 -> 길이가 긴 것 -> 대문자부터 -> 사전 순으로
        if a == b:
            return self.multiplier < other.multiplier
        elif len(a) != len(b):
            return len(a) > len(b)
        elif a.isupper() and b.islower():
            return True
        elif a.islower() and b.isupper():
            return False
        else:
            return a < b

    def __contains__(self, unit: UnitBase) -> bool:
        return self == unit

    def __repr__(self) -> str:
        ret = f"<{self.__class__.__name__}[{self.dimension}] '{self.symbol}'"
        if self.offset != 0:
            ret += f" offset={self.offset}"
        if self.multiplier != 1:
            ret += f" multiplier={self.multiplier}"
        return ret + ">"

    def __format__(self, format_spec: str) -> str:
        if format_spec == "":
            return self.symbol
        else:
            raise ValueError("Invalid format specification")

    def _repr_latex_(self) -> str:
        return f'$\\mathrm {{{self.latex_symbol}}}$'

    def expand(self):
        return self
    
    def si(self):
        return self

# %% ComplexUnit
class ComplexUnit(UnitBase):
    def __init__(self, records: ArithmeticDict[Unit], offset: Number = 0, multiplier: Number = 1):
        """
        :param records: A dictionary of units and their exponents
        """

        # set properties
        dimension = sum((unit.dimension * exponent for unit, exponent in records.items()), start=Dimension())
        offset = offset  # TODO: offset 자동 계산
        multiplier = multiplier * product((unit.multiplier ** exponent for unit, exponent in records.items()))
        depth = max((unit.depth for unit in records.keys()), default=0) + 1

        # call super constructor
        super().__init__(dimension, offset, multiplier, depth)

        # set records
        _records: dict[Unit, Number] = {}
        for unit, exponent in records.items():
            if exponent != 0:
                _records[unit] = exponent
                unit.multiplier = 1

        # optimize records
        self.records: ArithmeticDict[Unit] = ArithmeticDict[Unit](_records)

    # test: 테스트 필요
    def __format__(self, format_spec: str) -> str:
        precision: int | None = None

        if format_spec != "":
            match = re.match(r"^\.(\d+)f$", format_spec)

            if match:
                precision = int(match.group(1))
            else:
                raise ValueError(f"Invalid format specification '{format_spec}'")

        front = []
        back = []
        multiplier_string = pretty(self.multiplier, precision)

        for unit, exponent in self.records.items():
            if exponent > 0:
                if exponent == 1:
                    front.append(unit.symbol)
                else:
                    front.append(f"{unit.symbol}^{pretty(exponent)}")
            else:
                if exponent == -1:
                    back.append(unit.symbol)
                else:
                    back.append(f"{unit.symbol}^{pretty(-exponent)}")

        if front and back:
            formula = f'{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(front)}{SMALL_SPACE}/{SMALL_SPACE}{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(back)}'
            if self.multiplier != 1:
                formula = f"{multiplier_string}{SMALL_SPACE}{formula}"
        elif front:
            formula = f'{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(front)}'
            if self.multiplier != 1:
                formula = f"{multiplier_string}{SMALL_SPACE}{formula}"
        elif back:
            formula = f'{multiplier_string}{SMALL_SPACE}/{SMALL_SPACE}{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(back)}'
        else:
            formula = f'{multiplier_string}'

        return formula

    def _repr_latex_(self) -> str:
        front = []
        back = []
        multiplier_string = pretty(self.multiplier, LaTeX=True)

        for unit, exponent in self.records.items():
            if exponent > 0:
                if exponent == 1:
                    front.append(unit.symbol)
                else:
                    front.append(f"{unit.symbol}^{{{pretty(exponent)}}}")
            else:
                if exponent == -1:
                    back.append(unit.symbol)
                else:
                    back.append(f"{unit.symbol}^{{{pretty(-exponent)}}}")

        if front and back:
            formula = f'\\dfrac{{{MULTIPLY_SIGN_LATEX.join(front)}}}{{{MULTIPLY_SIGN_LATEX.join(back)}}}'
            if self.multiplier != 1:
                formula = f'{multiplier_string}{SMALL_SPACE_LATEX}{formula}'
        elif front:
            formula = f'{MULTIPLY_SIGN_LATEX.join(front)}'
            if self.multiplier != 1:
                formula = f'{multiplier_string}{SMALL_SPACE_LATEX}{formula}'
        elif back:
            formula = f'\\dfrac{{{multiplier_string}}}{{{MULTIPLY_SIGN_LATEX.join(back)}}}'
        else:
            formula = f'{multiplier_string}'

        return f'$\\mathrm {{{formula}}}$'

    def __repr__(self):
        ret = f"<ComplexUnit[{self.dimension}] '{self}'"
        if self.offset != 0:
            ret += f" offset={self.offset}"
        if self.multiplier != 1:
            ret += f" multiplier={self.multiplier}"
        return ret + ">"

    def __contains__(self, unit: UnitBase) -> bool:
        return unit in self.records

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        return ComplexUnit(deepcopy(self.records, memo), self.offset, self.multiplier)

    def expand(self):
        """
        records: {(depth 4): 2, (depth 2): 1, (depth 2): 2, (depth 3): 1}
        expanded: expand (depth 4) -> (depth 3), {(depth 3): 2, (depth 2): 1, (depth 2): 2, (depth 3): 1}
        expanded: expand (depth 3) -> (depth 2), {(depth 2): 2, (depth 2): 1, (depth 2): 2, (depth 3): 1}
        expanded: expand (depth 3) -> (depth 2), {(depth 2): 2, (depth 2): 1, (depth 2): 2, (depth 2): 1}

        function 'expand' is flatten the records by merging the same depth records
        """

        expanded = deepcopy(self.records)
        keys_sorted_by_depth = sorted(self.records.keys(), key=lambda x: x.depth, reverse=True)

        if len(keys_sorted_by_depth) > 0:
            most_key, most_value = keys_sorted_by_depth[0], self.records[keys_sorted_by_depth[0]]

            if most_key.depth != 0:
                most_key_expanded = most_key.expand()

                if isinstance(most_key_expanded, ComplexUnit):
                    for key, value in most_key_expanded.records.items():
                        expanded[key] += value * most_value
                else:
                    expanded[most_key_expanded] += most_value

                del expanded[most_key]

                return ComplexUnit(expanded, self.offset, self.multiplier * most_key_expanded.multiplier ** most_value)

        return ComplexUnit(expanded, self.offset, self.multiplier)

    def si(self):        
        _dict = ComplexUnit(ArithmeticDict())
        for unit, exponent in self.records.items():
            _dict *= unit.si() ** exponent
        
        _dict.multiplier *= self.multiplier
        return _dict

# %% FixedUnit
class FixedUnit(Unit):
    def __new__(cls, symbol: str, base: ComplexUnit, offset: Number = 0, multiplier: Number = 1, *args,
                **kwargs):
        key = (cls, symbol, base.dimension, base.offset, base.multiplier)

        if key not in cls._instances:
            cls._instances[key] = super(Unit, cls).__new__(cls)

        return cls._instances[key]

    def __init__(self, symbol: str, base: ComplexUnit, offset: Number = 0, multiplier: Number = 1, *, latex_symbol: str | None = None):
        super().__init__(symbol, base.dimension, offset, 1, latex_symbol=latex_symbol)

        base.multiplier *= multiplier   # FixedUnit의 multiplier는 항상 1, base의 multiplier에만 곱해준다.
        self.base = base
        self.depth = base.depth + 1

    def __contains__(self, unit: UnitBase) -> bool:
        return unit in self.base

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        return FixedUnit(self.symbol, deepcopy(self.base, memo), self.offset, self.multiplier, latex_symbol=self.latex_symbol)

    def expand(self):
        ret = self.base
        ret.multiplier *= self.multiplier
        return ret

    def si(self):
        return self.base.si()

# %% Quantity

@total_ordering
class Quantity:
    def __init__(self, value: Number, unit: U):
        """
        :param value: Number
        :param unit: bound of UnitBase
        """

        self.value = value * unit.multiplier
        self.unit = unit
        unit.multiplier = 1

    def __str__(self) -> str:
        return self.__format__("")

    def __repr__(self) -> str:
        return f"<Quantity {pretty(self.value)} {self.unit}>"

    def __format__(self, format_spec: str) -> str:
        return self.to_complex_unit().__format__(format_spec)

    def _repr_latex_(self) -> str:
        return self.to_complex_unit()._repr_latex_()

    def __eq__(self, other: 'Quantity | UnitBase | Number') -> bool:    # type: ignore
        return _eq(self, other)

    # TEST: __lt__ 테스트
    @overload
    def __lt__(self, other: 'Quantity') -> bool:
        if self.unit.dimension != other.unit.dimension:
            raise DimensionError(self.unit.dimension, other.unit.dimension, "Cannot compare quantities with different dimensions")

        return self.si().value < other.si().value

    @overload
    def __lt__(self, other: UnitBase) -> bool:
        if self.unit.dimension != other.dimension:
            raise DimensionError(self.unit.dimension, other.dimension, "Cannot compare quantities with different dimensions")

        # TODO: offset, 0K, 0C는 둘 다 0이지만 0K < 0C이다.
        return self.si().value < other.si().multiplier

    @overload
    def __lt__(self, other: Number) -> bool:
        if other == 0:
            # TEST: -A를 fix한 B라는 unit이 있으면 단순 multipler 비교만으로는 비교할 수 없다.
            return self.si().value < 0
        else:
            return NotImplemented

    @overload
    def __lt__(self, other) -> bool:
        return NotImplemented

    @dispatch
    def __lt__(self, other):
        pass

    def __add__(self, other: 'Quantity | UnitBase'):
        return _add(self, other)

    def __radd__(self, other: 'Quantity | UnitBase'):
        return self.__add__(other)

    def __sub__(self, other: 'Quantity | UnitBase'):
        return _sub(self, other)

    def __rsub__(self, other: 'Quantity | UnitBase'):
        return -self.__sub__(other)

    def __mul__(self, other: 'Quantity | UnitBase | Number'):
        return _mul(self, other)

    def __rmul__(self, other: 'Quantity | UnitBase | Number'):
        return self.__mul__(other)

    def __truediv__(self, other: 'Quantity | UnitBase | Number'):
        return _div(self, other)

    def __rtruediv__(self, other: 'Quantity | UnitBase | Number'):
        return self.__truediv__(other) ** -1

    def __pow__(self, exponent: Number):
        return _pow(self, exponent)

    def __pos__(self):
        return self

    def __neg__(self):
        return Quantity(-self.value, self.unit)

    def __abs__(self) -> 'Quantity':
        return Quantity(abs(self.value), self.unit)

    def __contains__(self, unit: UnitBase) -> bool:
        return unit in self.unit

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        return Quantity(self.value, deepcopy(self.unit, memo))

    def to_complex_unit(self) -> ComplexUnit:
        _cp = self.unit ** 1
        _cp.multiplier = self.value
        return _cp

    def expand(self):
        _cp = self.to_complex_unit().expand()
        return Quantity(1, _cp)

    def si(self):
        _cp = self.to_complex_unit().si()
        return Quantity(1, _cp)

    def to(self, other: 'UnitBase | Quantity') -> 'Quantity':
        _cp = self.to_complex_unit().to(other.to_complex_unit() if isinstance(other, Quantity) else other)
        return Quantity(1, _cp)

# %% _eq
@overload
def _eq(a: ComplexUnit, b: Number) -> bool:
    if a.multiplier == 0:
        return b == 0
    elif a.dimension == dimensionless:
        return a.si().multiplier == b
    else:
        return NotImplemented

@overload
def _eq(a: FixedUnit, b: Number) -> bool:
    if a.multiplier == 0:
        return b == 0
    elif a.dimension == dimensionless:
        return a.si().multiplier == b
    else:
        return NotImplemented

@overload
def _eq(a: UnitBase, b: Number) -> bool:
    if a.multiplier == 0:
        return b == 0
    elif a.dimension == dimensionless:
        return a.multiplier == b
    else:
        return NotImplemented

@overload
def _eq(a: Number, b: UnitBase) -> bool:
    return _eq(b, a)

@overload
def _eq(a: ComplexUnit, b: ComplexUnit, except_multiplier=False) -> bool:
    if except_multiplier:
        return a.dimension == b.dimension and a.offset == b.offset and a.si().records == b.si().records
    elif a.multiplier == 0 or b.multiplier == 0:   # todo: offset 고려
        return a.multiplier == b.multiplier
    else:
        return a.dimension == b.dimension and a.offset == b.offset and a.multiplier == b.multiplier and a.si().records == b.si().records

@overload
def _eq(a: ComplexUnit, b: Unit, except_multiplier=False) -> bool:
    return _eq(a.si(), (b**1).si(), except_multiplier)

@overload
def _eq(a: Unit, b: ComplexUnit, except_multiplier=False) -> bool:
    return _eq(b, a)

@overload
def _eq(a: Unit, b: Unit, except_multiplier=False) -> bool:    
    if except_multiplier:
        return a.dimension == b.dimension and a.offset == b.offset
    elif a.multiplier == 0 or b.multiplier == 0:   # todo: offset 고려
        return a.multiplier == b.multiplier
    else:
        return a.dimension == b.dimension and a.offset == b.offset and a.multiplier == b.multiplier

@overload
def _eq(a: Quantity, b: Quantity) -> bool:
    return _eq(a.to_complex_unit(), b.to_complex_unit())

@overload
def _eq(a: Quantity, b: UnitBase | Number) -> bool:
    return _eq(a.to_complex_unit(), b)

@overload
def _eq(a, b, except_multiplier=False) -> bool:
    return NotImplemented

@dispatch
def _eq(a, b, except_multiplier=False):
    pass

# %% _add
@overload
def _add(a: ComplexUnit, b: ComplexUnit) -> ComplexUnit:
    if a.dimension != b.dimension:
        raise DimensionError(a.dimension, b.dimension, "Cannot add units with different dimensions")

    if a.depth > b.depth:
        a, b = b, a
    
    a_, b_ = a.si(), b.si()
    ret = ComplexUnit(ArithmeticDict(a.records))
    ret.multiplier = (a_.multiplier + b_.multiplier) / (a_.multiplier / a.multiplier if a.multiplier != 0 else 1)
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _add(a: ComplexUnit, b: Unit) -> ComplexUnit:
    if a.dimension != b.dimension:
        raise DimensionError(a.dimension, b.dimension, "Cannot add units with different dimensions")

    # TODO: offset
    a_, b_ = a.si(), b.si()
    ret = ComplexUnit(ArithmeticDict({b: 1}))
    ret.multiplier = (a_.multiplier + b_.multiplier) / (b_.multiplier / b.multiplier)   # TEST 필요
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _add(a: Unit, b: ComplexUnit) -> ComplexUnit:
    if a.dimension != b.dimension:
        raise DimensionError(a.dimension, b.dimension, "Cannot add units with different dimensions")

    # TODO: offset
    a_, b_ = a.si(), b.si()
    ret = ComplexUnit(ArithmeticDict({a: 1}))
    ret.multiplier = (a_.multiplier + b_.multiplier) / (a_.multiplier / a.multiplier if a.multiplier != 0 else 1)   # TEST 필요
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _add(a: Unit, b: Unit) -> ComplexUnit:
    if a.dimension != b.dimension:
        raise DimensionError(a.dimension, b.dimension, "Cannot add units with different dimensions")

    # TODO: offset
    if a.depth > b.depth:
        a, b = b, a
    
    a_, b_ = a.si(), b.si()
    ret = ComplexUnit(ArithmeticDict({a: 1}))
    ret.multiplier = (a_.multiplier + b_.multiplier) / (a_.multiplier / a.multiplier if a.multiplier != 0 else 1)   # TEST 필요
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _add(a: Quantity, b: Quantity) -> Quantity:
    return Quantity(1, _add(a.to_complex_unit(), b.to_complex_unit()))

@overload
def _add(a: Quantity, b: UnitBase) -> Quantity:
    return Quantity(1, _add(a.to_complex_unit(), b))

@overload
def _add(a: Quantity, b: Number) -> Quantity:
    if b == 0:
        return a
    else:
        return NotImplemented

@overload
def _add(a, b):
    return NotImplemented

@dispatch
def _add(a, b):
    pass

# %% _sub
@overload
def _sub(a: ComplexUnit, b: ComplexUnit) -> ComplexUnit:
    if a.dimension != b.dimension:
        raise DimensionError(a.dimension, b.dimension, "Cannot subtract units with different dimensions")

    swap = False
    if a.depth > b.depth:
        a, b = b, a
        swap = True

    a_, b_ = a.si(), b.si()
    ret = ComplexUnit(ArithmeticDict(a.records))
    ret.multiplier = (a_.multiplier - b_.multiplier) / (a_.multiplier / a.multiplier if a.multiplier != 0 else 1)
    if swap:
        ret.multiplier *= -1

    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _sub(a: ComplexUnit, b: Unit) -> ComplexUnit:
    if a.dimension != b.dimension:
        raise DimensionError(a.dimension, b.dimension, "Cannot subtract units with different dimensions")

    a_, b_ = a.si(), b.si()
    ret = ComplexUnit(ArithmeticDict({b: 1}))
    ret.multiplier = (a_.multiplier - b_.multiplier) / (b_.multiplier / b.multiplier if b.multiplier != 0 else 1)
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _sub(a: Unit, b: ComplexUnit) -> ComplexUnit:
    if a.dimension != b.dimension:
        raise DimensionError(a.dimension, b.dimension, "Cannot subtract units with different dimensions")

    a_, b_ = a.si(), b.si()
    ret = ComplexUnit(ArithmeticDict({a: 1}))
    ret.multiplier = (a_.multiplier - b_.multiplier) / (a_.multiplier / a.multiplier if a.multiplier != 0 else 1)
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _sub(a: Unit, b: Unit) -> ComplexUnit:
    if a.dimension != b.dimension:
        raise DimensionError(a.dimension, b.dimension, "Cannot subtract units with different dimensions")

    swap = False
    if a.depth > b.depth:
        a, b = b, a
        swap = True

    ret = ComplexUnit(ArithmeticDict({a: 1}))
    ret.multiplier = (a.multiplier - b.multiplier) / (a.multiplier / b.multiplier if b.multiplier != 0 else 1)
    if swap:
        ret.multiplier *= -1

    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _sub(a: Quantity, b: Quantity) -> Quantity:
    return Quantity(1, _sub(a.to_complex_unit(), b.to_complex_unit()))

@overload
def _sub(a: Quantity, b: UnitBase) -> Quantity:
    return Quantity(1, _sub(a.to_complex_unit(), b))

@overload
def _sub(a: Quantity, b: Number) -> Quantity:
    if b == 0:
        return a
    else:
        return NotImplemented

@overload
def _sub(a, b):
    return NotImplemented

@dispatch
def _sub(a, b):
    pass

# %% _mul
@overload
def _mul(a: ComplexUnit, b: ComplexUnit) -> ComplexUnit:
    merged_records = deepcopy(a.records)
    for key, value in b.records.items():
        merged_records[key] += value

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier * b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

# TODO: offset
@overload
def _mul(a: ComplexUnit, b: Unit) -> ComplexUnit:
    merged_records = deepcopy(a.records)
    merged_records[b] += 1

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier * b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _mul(a: Unit, b: ComplexUnit) -> ComplexUnit:
    merged_records = deepcopy(b.records)
    merged_records[a] += 1

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier * b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _mul(a: Unit, b: Unit) -> ComplexUnit:
    # if _eq(a, b):
    #     ret = ComplexUnit(ArithmeticDict({a: 2}))
    # elif _eq(a, b, except_multiplier=True):
    #     ret = ComplexUnit(ArithmeticDict({a: 2}))
    #     ret.multiplier = b.multiplier / a.multiplier
    # else:
    #     ret = ComplexUnit(ArithmeticDict({a: 1, b: 1}))

    d = ArithmeticDict[Unit]()
    d[a] += 1
    d[b] += 1

    ret = ComplexUnit(d)    # multiplier 계산은 생성자에서 자동으로 처리
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@overload
def _mul(a: UnitBase, b: Number) -> Quantity:
    return Quantity(b, a)

@overload
def _mul(a: Number, b: UnitBase) -> Quantity:
    return Quantity(a, b)

@overload
def _mul(a: UnitBase, b: ArrayLike) -> list[Quantity] | ndarray:
    if isinstance(b, ndarray):
        return array(b) * a
    else:
        return [i * a for i in b]

@overload
def _mul(a: ArrayLike, b: UnitBase) -> list[Quantity] | ndarray:
    if isinstance(a, ndarray):
        return array(a) * b
    else:
        return [i * b for i in a]

@overload
def _mul(a: Quantity, b: Quantity) -> Quantity:
    return Quantity(1, _mul(a.to_complex_unit(), b.to_complex_unit()))

@overload
def _mul(a: Quantity, b: UnitBase) -> Quantity:
    return Quantity(1, _mul(a.to_complex_unit(), b))

@overload
def _mul(a: Quantity, b: Number) -> Quantity:
    return Quantity(a.value * b, a.unit)

@overload
def _mul(a, b):
    return NotImplemented

@dispatch
def _mul(a, b):
    pass

# %% _div
@overload
def _div(a: ComplexUnit | Unit, b: ComplexUnit | Unit) -> ComplexUnit:
    return a * b ** -1

@overload
def _div(a: UnitBase, b: Number) -> Quantity:
    return Quantity(1 / b, a)

@overload
def _div(a: Number, b: UnitBase) -> Quantity:
    return Quantity(a, b ** -1)

@overload
def _div(a: ArrayLike, b: UnitBase) -> list[Quantity] | ndarray:
    if isinstance(a, ndarray):
        return array(a) / b
    else:
        return [i / b for i in a]

@overload
def _div(a: Quantity, b: Quantity) -> Quantity:
    return Quantity(1, _div(a.to_complex_unit(), b.to_complex_unit()))

@overload
def _div(a: Quantity, b: UnitBase) -> Quantity:
    return Quantity(1, _div(a.to_complex_unit(), b))

@overload
def _div(a: Quantity, b: Number) -> Quantity:
    return Quantity(a.value / b, a.unit)

@overload
def _div(a, b):
    return NotImplemented

@dispatch
def _div(a, b):
    pass

# %% _pow
@overload
def _pow(a: ComplexUnit, exponent: Number) -> ComplexUnit:
    ret = ComplexUnit(ArithmeticDict({unit: exp * exponent for unit, exp in a.records.items()}))
    ret.multiplier = a.multiplier ** exponent
    ret.depth = a.depth + 1
    return ret

@overload
def _pow(a: Unit, exponent: Number) -> ComplexUnit:
    ret = ComplexUnit(ArithmeticDict({a: exponent}))
    ret.multiplier = a.multiplier ** exponent
    ret.depth = a.depth + 1
    return ret

@overload
def _pow(a: Quantity, exponent: Number) -> Quantity:
    return Quantity(1, _pow(a.to_complex_unit(), exponent))

@overload
def _pow(a, exponent):
    return NotImplemented

@dispatch
def _pow(a, exponent):
    pass

# %%

__all__ = ['Unit', 'FixedUnit']
