from abc import abstractmethod
from copy import deepcopy

from multipledispatch import dispatch
from attrs import define
from siunits.utils import commutative, ArithmeticDict, product, pretty, SMALL_SPACE, MULTIPLY_SIGN, SMALL_SPACE_LATEX, \
    MULTIPLY_SIGN_LATEX
from siunits.dimension import Dimension, DimensionMismatchError

# %% UnitBase
@commutative
@define(hash=False, eq=False)
class UnitBase:
    dimension: Dimension
    offset: int | float = 0
    multiplier: int | float = 1
    depth: int = 0

    def __eq__(self, other):
        return _eq(self, other)

    def __add__(self, other):
        return _add(self, other)

    def __sub__(self, other):
        return _sub(self, other)

    def __mul__(self, other):
        return _mul(self, other)

    def __truediv__(self, other):
        return _div(self, other)

    def __pow__(self, exponent):
        return _pow(self, exponent)

    @abstractmethod
    def __deepcopy__(self, memo=None):
        pass

    @abstractmethod
    def __str__(self) -> str:
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

    def to(self, other: 'UnitBase') -> 'UnitBase':
        # TODO: Implement conversion
        if self.dimension != other.dimension:
            raise DimensionMismatchError(self.dimension, other.dimension, "Cannot convert units with different dimensions")

        # atm**2.to(atm*Pa) -> 101325 atm*Pa
        # multiplier도 고려해야함

        ret = deepcopy(other**1)
        ret.multiplier = self.si().multiplier / other.si().multiplier
        return ret

# %% Unit
class Unit(UnitBase):
    _instances: dict[tuple, 'Unit'] = {}

    def __new__(cls, symbol: str, dimension: Dimension, offset: int | float = 0, multiplier: int | float = 1, *args,
                **kwargs):
        key = (cls, symbol, dimension, offset, multiplier)

        if key not in cls._instances:
            cls._instances[key] = super().__new__(cls)

        return cls._instances[key]

    def __init__(self, symbol: str, dimension: Dimension, offset: int | float = 0, multiplier: int | float = 1, *, latex_symbol: str | None = None):
        super().__init__(dimension, offset, multiplier)
        self.symbol = symbol
        self.latex_symbol = symbol if latex_symbol is None else latex_symbol

    def __str__(self) -> str:
        return self.symbol

    def _repr_latex_(self) -> str:
        return f'$\\mathrm {{{self.latex_symbol}}}$'

    def __repr__(self) -> str:
        ret = f"<Unit[{self.dimension}] '{self.symbol}'"
        if self.offset != 0:
            ret += f" offset={self.offset}"
        if self.multiplier != 1:
            ret += f" multiplier={self.multiplier}"
        return ret + ">"

    def __hash__(self) -> int:  # type: ignore
        return hash((self.symbol, self.dimension, self.offset, self.multiplier))

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

    def __class_getitem__(cls, symbol: str) -> 'Unit | list[Unit]':
        found: list['Unit'] = []
        for k in cls._instances:
            if k[0] == symbol:
                found.append(cls._instances[k])

        if len(found) == 0:
            raise KeyError(f"No unit with symbol '{symbol}'")
        elif len(found) == 1:
            return found[0]
        else:
            return found

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        return Unit(self.symbol, self.dimension, self.offset, self.multiplier, latex_symbol=self.latex_symbol)

    def expand(self):
        return self
    
    def si(self):
        return self

# %% ComplexUnit
class ComplexUnit(UnitBase):
    def __init__(self, records: ArithmeticDict[Unit], offset: int | float = 0, multiplier: int | float = 1):
        """
        :param records: A dictionary of units and their exponents
        """

        # set properties
        dimension = sum((unit.dimension * exponent for unit, exponent in records.items()), start=Dimension())
        offset = offset  # TODO: Implement offset automatically
        multiplier = multiplier * product((unit.multiplier ** exponent for unit, exponent in records.items()))
        depth = max((unit.depth for unit in records.keys()), default=0) + 1

        # call super constructor
        super().__init__(dimension, offset, multiplier, depth)

        # set records
        _records: dict[Unit, int | float] = {}
        for unit, exponent in records.items():
            if exponent != 0:
                _records[unit] = exponent
                unit.multiplier = 1

        # optimize records
        self.records: ArithmeticDict[Unit] = ArithmeticDict[Unit](_records)

    def __str__(self) -> str:
        front = []
        back = []

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
                formula = f"{pretty(self.multiplier)}{SMALL_SPACE}{formula}"
        elif front:
            formula = f'{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(front)}'
            if self.multiplier != 1:
                formula = f"{pretty(self.multiplier)}{SMALL_SPACE}{formula}"
        elif back:
            formula = f'{pretty(self.multiplier)}{SMALL_SPACE}/{SMALL_SPACE}{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(back)}'
        else:
            formula = f'{pretty(self.multiplier)}'

        return formula

    def _repr_latex_(self) -> str:
        front = []
        back = []

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
            formula = f'\\dfrac{{{MULTIPLY_SIGN_LATEX.join(front)}}}{{{MULTIPLY_SIGN_LATEX.join(back)}}}'
            if self.multiplier != 1:
                formula = f'{pretty(self.multiplier)}{SMALL_SPACE_LATEX}{formula}'
        elif front:
            formula = f'{MULTIPLY_SIGN_LATEX.join(front)}'
            if self.multiplier != 1:
                formula = f'{pretty(self.multiplier)}{SMALL_SPACE_LATEX}{formula}'
        elif back:
            formula = f'\\dfrac{{{pretty(self.multiplier)}}}{{{MULTIPLY_SIGN_LATEX.join(back)}}}'
        else:
            formula = f'{pretty(self.multiplier)}'

        return f'$\\mathrm {{{formula}}}$'

    def __repr__(self):
        ret = f"<ComplexUnit[{self.dimension}] '{self}'"
        if self.offset != 0:
            ret += f" offset={self.offset}"
        if self.multiplier != 1:
            ret += f" multiplier={self.multiplier}"
        return ret + ">"

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
        keys_sorted_by_depth: list[Unit] = sorted(self.records.keys(), key=lambda x: x.depth, reverse=True)

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
    def __new__(cls, symbol: str, base: ComplexUnit, offset: int | float = 0, multiplier: int | float = 1, *args,
                **kwargs):
        key = (cls, symbol, base.dimension, base.offset, base.multiplier)

        if key not in cls._instances:
            cls._instances[key] = super(Unit, cls).__new__(cls)

        return cls._instances[key]

    def __init__(self, symbol: str, base: ComplexUnit, offset: int | float = 0, multiplier: int | float = 1, *, latex_symbol: str | None = None):
        super().__init__(symbol, base.dimension, offset, 1, latex_symbol=latex_symbol)

        base.multiplier *= multiplier
        self.base = base
        self.depth = base.depth

    def __repr__(self):
        ret = f"<FixedUnit[{self.dimension}] '{self.symbol}'"
        if self.offset != 0:
            ret += f" offset={self.offset}"
        if self.multiplier != 1:
            ret += f" multiplier={self.multiplier}"
        return ret + ">"

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

# %% _eq
@dispatch(ComplexUnit, ComplexUnit)
def _eq(a, b, except_multiplier=False) -> bool:
    if except_multiplier:
        return a.dimension == b.dimension and a.offset == b.offset and a.records == b.records
    else:
        return a.dimension == b.dimension and a.offset == b.offset and a.multiplier == b.multiplier and a.records == b.records

@dispatch(ComplexUnit, Unit)
def _eq(a, b, except_multiplier=False) -> bool:
    if except_multiplier:
        return a.dimension == b.dimension and a.offset == b.offset and a.records == {b: 1}
    else:
        return a.dimension == b.dimension and a.offset == b.offset and a.multiplier == b.multiplier and a.records == {
            b: 1}

@dispatch(Unit, ComplexUnit)
def _eq(a, b, except_multiplier=False) -> bool:
    if except_multiplier:
        return a.dimension == b.dimension and a.offset == b.offset and b.records == {a: 1}
    else:
        return a.dimension == b.dimension and a.offset == b.offset and a.multiplier == b.multiplier and b.records == {
            a: 1}

@dispatch(Unit, Unit)
def _eq(a, b, except_multiplier=False) -> bool:
    if except_multiplier:
        return a.dimension == b.dimension and a.offset == b.offset and a.symbol == b.symbol
    else:
        return a.dimension == b.dimension and a.offset == b.offset and a.multiplier == b.multiplier and a.symbol == b.symbol

@dispatch(object, object)
def _eq(a, b, except_multiplier=False) -> bool:
    return False

# %% _add
@dispatch(ComplexUnit, ComplexUnit)
def _add(a, b):
    if a.dimension != b.dimension:
        raise DimensionMismatchError(a.dimension, b.dimension, "Cannot add units with different dimensions")

    ret = ComplexUnit(ArithmeticDict(a.records))
    ret.multiplier = a.multiplier + b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(ComplexUnit, Unit)
def _add(a, b):
    if a.dimension != b.dimension:
        raise DimensionMismatchError(a.dimension, b.dimension, "Cannot add units with different dimensions")

    # TODO: offset, multiplier 고려해서 dimension이 같을 때만 더하기 가능하도록 수정, 지금은 완전히 같은 단위라고 취급하고 더하게 함
    ret = ComplexUnit(ArithmeticDict({b: 1}))
    ret.multiplier = a.multiplier + b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(Unit, ComplexUnit)
def _add(a, b):
    if a.dimension != b.dimension:
        raise DimensionMismatchError(a.dimension, b.dimension, "Cannot add units with different dimensions")

    # TODO: offset, multiplier 고려해서 dimension이 같을 때만 더하기 가능하도록 수정, 지금은 완전히 같은 단위라고 취급하고 더하게 함
    ret = ComplexUnit(ArithmeticDict({a: 1}))
    ret.multiplier = a.multiplier + b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(Unit, Unit)
def _add(a, b):
    if a.dimension != b.dimension:
        raise DimensionMismatchError(a.dimension, b.dimension, "Cannot add units with different dimensions")

    # TODO: offset, multiplier 고려해서 dimension이 같을 때만 더하기 가능하도록 수정, 지금은 완전히 같은 단위라고 취급하고 더하게 함
    ret = ComplexUnit(ArithmeticDict({a: 1}))
    ret.multiplier = a.multiplier + b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(object, object)
def _add(a, b):
    return NotImplemented

# %% _sub
@dispatch(ComplexUnit, ComplexUnit)
def _sub(a, b):
    if a.dimension != b.dimension:
        raise DimensionMismatchError(a.dimension, b.dimension, "Cannot subtract units with different dimensions")

    ret = ComplexUnit(ArithmeticDict(a.records))
    ret.multiplier = a.multiplier - b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(ComplexUnit, Unit)
def _sub(a, b):
    if a.dimension != b.dimension:
        raise DimensionMismatchError(a.dimension, b.dimension, "Cannot subtract units with different dimensions")

    ret = ComplexUnit(ArithmeticDict({b: 1}))
    ret.multiplier = a.multiplier - b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(Unit, ComplexUnit)
def _sub(a, b):
    if a.dimension != b.dimension:
        raise DimensionMismatchError(a.dimension, b.dimension, "Cannot subtract units with different dimensions")

    ret = ComplexUnit(ArithmeticDict({a: 1}))
    ret.multiplier = a.multiplier - b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(Unit, Unit)
def _sub(a, b):
    if a.dimension != b.dimension:
        raise DimensionMismatchError(a.dimension, b.dimension, "Cannot subtract units with different dimensions")

    ret = ComplexUnit(ArithmeticDict({a: 1}))
    ret.multiplier = a.multiplier - b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(object, object)
def _sub(a, b):
    return NotImplemented

# %% _mul
@dispatch(ComplexUnit, ComplexUnit)
def _mul(a, b):
    merged_records = deepcopy(a.records)
    for key, value in b.records.items():
        merged_records[key] += value

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier * b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

# TODO: offset도 따로 고려해야 함, dimension이 같은 지 비교하는게 더 옳아보이는데 일단은 이렇게 놔둠
@dispatch(ComplexUnit, Unit)
def _mul(a, b):
    merged_records = deepcopy(a.records)
    merged_records[b] += 1

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier * b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(Unit, ComplexUnit)
def _mul(a, b):
    merged_records = deepcopy(b.records)
    merged_records[a] += 1

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier * b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(Unit, Unit)
def _mul(a, b):
    if _eq(a, b):
        ret = ComplexUnit(ArithmeticDict({a: 2}))
    elif _eq(a, b, except_multiplier=True):
        ret = ComplexUnit(ArithmeticDict({a: 2}))
        ret.multiplier = b.multiplier / a.multiplier
    else:
        ret = ComplexUnit(ArithmeticDict({a: 1, b: 1}))

    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(object, object)
def _mul(a, b):
    return NotImplemented

# %% _div
@dispatch(ComplexUnit, ComplexUnit)
def _div(a, b):
    merged_records = deepcopy(a.records)
    for key, value in b.records.items():
        merged_records[key] -= value

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier / b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(ComplexUnit, Unit)
def _div(a, b):
    merged_records = deepcopy(a.records)
    merged_records[b] -= 1

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier / b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(Unit, ComplexUnit)
def _div(a, b):
    merged_records = -b.records
    merged_records[a] += 1

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier / b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(Unit, Unit)
def _div(a, b):
    if _eq(a, b):
        ret = ComplexUnit(ArithmeticDict({a: 0}))
    elif _eq(a, b, except_multiplier=True):
        ret = ComplexUnit(ArithmeticDict({a: 0}))
        ret.multiplier = a.multiplier / b.multiplier
    else:
        ret = ComplexUnit(ArithmeticDict({a: 1, b: -1}))

    ret.depth = max(a.depth, b.depth) + 1
    return ret

@dispatch(object, object)
def _div(a, b):
    return NotImplemented

# %% _pow
@dispatch(ComplexUnit, (int, float))
def _pow(a, exponent):
    ret = ComplexUnit(ArithmeticDict({unit: exp * exponent for unit, exp in a.records.items()}))
    ret.multiplier = a.multiplier ** exponent
    ret.depth = a.depth + 1
    return ret

@dispatch(Unit, (int, float))
def _pow(a, exponent):
    ret = ComplexUnit(ArithmeticDict({a: exponent}))
    ret.multiplier = a.multiplier ** exponent
    ret.depth = a.depth + 1
    return ret

@dispatch(object, object)
def _pow(a, exponent):
    return NotImplemented

# %%
