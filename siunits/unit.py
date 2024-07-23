from abc import abstractmethod
from copy import deepcopy
from multipledispatch import dispatch  # type: ignore
from attrs import define
from siunits.utils import commutative, ArithmeticDict, Multitone, product, pretty, SMALL_SPACE, \
    MULTIPLY_SIGN  # type: ignore
from siunits.dimension import Dimension, DimensionMismatchError  # type: ignore

@commutative
@define(hash=False)
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
    def __str__(self) -> str:
        pass

    @abstractmethod
    def _repr_latex_(self) -> str:
        pass

class Unit(UnitBase, metaclass=Multitone):
    def __init__(self, symbol: str, dimension: Dimension, offset: int | float = 0, multiplier: int | float = 1):
        super().__init__(dimension, offset, multiplier)
        self.symbol = symbol

    def __str__(self) -> str:
        return self.symbol

    def _repr_latex_(self) -> str:
        return f'$\\mathrm {{{self.symbol}}}$'

    def __repr__(self) -> str:
        return f"Unit('{self.symbol}', {self.dimension}, offset={self.offset}, multiplier={self.multiplier})"

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

    def __class_getitem__(cls, symbol: str) -> 'Unit  | list[Unit]':
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

class ComplexUnit(UnitBase):
    def __init__(self, records: ArithmeticDict[Unit], offset: int | float = 0, multiplier: int | float = 1):
        """
        :param records: A dictionary of units and their exponents
        """

        # set properties
        dimension = sum((unit.dimension * exponent for unit, exponent in records.items()), start=Dimension())
        offset = offset  # TODO: Implement offset automatically
        multiplier = multiplier
        depth = max((unit.depth for unit in records.keys()), default=0) + 1

        # call super constructor
        super().__init__(dimension, offset, multiplier, depth)

        # optimize records
        self.records: ArithmeticDict[Unit] = ArithmeticDict({unit: exponent for unit, exponent in records.items() if exponent != 0})

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
        elif front:
            formula = f'{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(front)}'
        elif back:
            formula = f'1{SMALL_SPACE}/{SMALL_SPACE}{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(back)}'
        else:
            formula = '1'

        if self.multiplier == 1:
            return formula
        else:
            return f"{pretty(self.multiplier)}{SMALL_SPACE}{formula}"

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

        MULTIPLY_SIGN_ = r' \cdot '
        SMALL_SPACE_ = r' \, '

        if front and back:
            formula = f'\\dfrac{{{MULTIPLY_SIGN_.join(front)}}}{{{MULTIPLY_SIGN_.join(back)}}}'
        elif front:
            formula = f'{MULTIPLY_SIGN_.join(front)}'
        elif back:
            formula = f'\\dfrac{{1}}{{{MULTIPLY_SIGN_.join(back)}}}'
        else:
            formula = '1'

        if self.multiplier == 1:
            return f'$\\mathrm {{{formula}}}$'
        else:
            return f'$\\mathrm {{{pretty(self.multiplier)}{SMALL_SPACE_}{formula}}}$'

    def __repr__(self):
        return f"ComplexUnit({self}, offset={self.offset}, multiplier={self.multiplier})"

########### _eq ###########

# TODO: except_offset 추가

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

########### _add ###########

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

########### _sub ###########

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

########### _mul ###########

# TODO: offset도 따로 고려해야 함, dimension이 같은 지 비교하는게 더 옳아보이는데 일단은 이렇게 놔둠
@dispatch(ComplexUnit, ComplexUnit)
def _mul(a, b):
    merged_records = deepcopy(a.records)
    for key, value in b.records.items():
        merged_records[key] += value

    ret = ComplexUnit(ArithmeticDict(merged_records))
    ret.multiplier = a.multiplier * b.multiplier
    ret.depth = max(a.depth, b.depth) + 1
    return ret

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

########### _div ###########

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

########### _pow ###########

@dispatch(ComplexUnit, (int, float))
def _pow(a, exponent):
    ret = ComplexUnit(ArithmeticDict({unit: exp * exponent for unit, exp in a.records.items()}))
    ret.depth = a.depth + 1
    return ret

@dispatch(Unit, (int, float))
def _pow(a, exponent):
    ret = ComplexUnit(ArithmeticDict({a: exponent}))
    ret.depth = a.depth + 1
    return ret

@dispatch(object, object)
def _pow(a, exponent):
    return NotImplemented

############################

class SI:
    kg = Unit('kg', Dimension(mass=1))
    m = Unit('m', Dimension(length=1))
    s = Unit('s', Dimension(time=1))
    A = Unit('A', Dimension(current=1))
    K = Unit('K', Dimension(temperature=1))
    mol = Unit('mol', Dimension(amount=1))
    cd = Unit('cd', Dimension(intensity=1))

    def __init__(self):
        raise TypeError("Cannot instantiate this class")
