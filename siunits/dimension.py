from siunits.utils import ArithmeticDict, pretty, SMALL_SPACE, MULTIPLY_SIGN, MULTIPLY_SIGN_LATEX
from attrs import define, asdict

# @commutative
@define(frozen=True, hash=True)
class Dimension:
    length: int | float = 0
    mass: int | float = 0
    time: int | float = 0
    current: int | float = 0
    temperature: int | float = 0
    amount: int | float = 0
    intensity: int | float = 0

    def __add__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(length=self.length + other.length, mass=self.mass + other.mass, time=self.time + other.time,
                         current=self.current + other.current, temperature=self.temperature + other.temperature,
                         amount=self.amount + other.amount, intensity=self.intensity + other.intensity)

    def __sub__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(length=self.length - other.length, mass=self.mass - other.mass, time=self.time - other.time,
                         current=self.current - other.current, temperature=self.temperature - other.temperature,
                         amount=self.amount - other.amount, intensity=self.intensity - other.intensity)

    def __mul__(self, other: 'Dimension | int | float') -> 'Dimension':
        if isinstance(other, int | float):
            return Dimension(length=self.length * other, mass=self.mass * other, time=self.time * other,
                             current=self.current * other, temperature=self.temperature * other,
                             amount=self.amount * other, intensity=self.intensity * other)
        else:
            return Dimension(length=self.length * other.length, mass=self.mass * other.mass,
                             time=self.time * other.time,
                             current=self.current * other.current, temperature=self.temperature * other.temperature,
                             amount=self.amount * other.amount, intensity=self.intensity * other.intensity)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other: 'Dimension | int | float') -> 'Dimension':
        if isinstance(other, int | float):
            return Dimension(length=self.length / other, mass=self.mass / other, time=self.time / other,
                             current=self.current / other, temperature=self.temperature / other,
                             amount=self.amount / other, intensity=self.intensity / other)
        else:
            return Dimension(length=self.length / other.length, mass=self.mass / other.mass,
                             time=self.time / other.time,
                             current=self.current / other.current, temperature=self.temperature / other.temperature,
                             amount=self.amount / other.amount, intensity=self.intensity / other.intensity)

    def __str__(self) -> str:
        symbols = {
            "length": "L",
            "mass": "M",
            "time": "T",
            "current": "I",
            "temperature": "Θ",
            "amount": "N",
            "intensity": "J"
        }

        front = []
        back = []

        for k, v in asdict(self).items():
            if v > 0:
                if v == 1:
                    front.append(symbols[k])
                else:
                    front.append(f"{symbols[k]}^{pretty(v)}")
            elif v < 0:
                if v == -1:
                    back.append(symbols[k])
                else:
                    back.append(f"{symbols[k]}^{pretty(-v)}")

        if front and back:
            formula = f'{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(front)}{SMALL_SPACE}/{SMALL_SPACE}{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(back)}'
        elif front:
            formula = f'{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(front)}'
        elif back:
            formula = f'1{SMALL_SPACE}/{SMALL_SPACE}{(SMALL_SPACE + MULTIPLY_SIGN + SMALL_SPACE).join(back)}'
        else:
            formula = '1'

        return formula

    def __repr__(self) -> str:
        return f"<Dimension [{self}]>"

    def _repr_latex_(self) -> str:
        symbols = {
            "length": "L",
            "mass": "M",
            "time": "T",
            "current": "I",
            "temperature": "\\theta",
            "amount": "N",
            "intensity": "J"
        }

        front = []
        back = []

        for k, v in asdict(self).items():
            if v > 0:
                if v == 1:
                    front.append(symbols[k])
                else:
                    front.append(f"{symbols[k]}^{pretty(v)}")
            elif v < 0:
                if v == -1:
                    back.append(symbols[k])
                else:
                    back.append(f"{symbols[k]}^{pretty(-v)}")

        if front and back:
            formula = f'\\dfrac{{{MULTIPLY_SIGN_LATEX.join(front)}}}{{{MULTIPLY_SIGN_LATEX.join(back)}}}'
        elif front:
            formula = f'{MULTIPLY_SIGN_LATEX.join(front)}'
        elif back:
            formula = f'\\dfrac{{1}}{{{MULTIPLY_SIGN_LATEX.join(back)}}}'
        else:
            formula = '1'

        return f'$\\mathrm{{Dimension\\left[ {formula} \\right]}}$'

dimensionless = Dimension()

class DimensionMismatchError(ValueError):
    def __init__(self, dim1: Dimension, dim2: Dimension, message: str = 'Dimension mismatch') -> None:
        super().__init__(f"{message}: {dim1} and {dim2}")

__all__ = ['Dimension', 'DimensionMismatchError', 'dimensionless']
