from siunits.types import Unit, FixedUnit
from siunits.dimension import Dimension

kg = Unit('kg', Dimension(mass=1))
m = Unit('m', Dimension(length=1))
s = Unit('s', Dimension(time=1))
A = Unit('A', Dimension(current=1))
K = Unit('K', Dimension(temperature=1))
mol = Unit('mol', Dimension(amount=1))
cd = Unit('cd', Dimension(intensity=1))

cm = FixedUnit('cm', m**1, multiplier=1e-2)
g = FixedUnit('g', kg**1, multiplier=1e-3)
mg = FixedUnit('mg', g**1, multiplier=1e-3)
minute = FixedUnit('min', s**1, multiplier=60)
h = FixedUnit('h', s**1, multiplier=3600)
N = FixedUnit('N', kg * m / s**2)
Pa = FixedUnit('Pa', N / m**2)
atm = FixedUnit('atm', Pa**1, multiplier=101325)
L = FixedUnit('L', cm**3, multiplier=1000)
J = FixedUnit('J', N * m)
cal = FixedUnit('cal', J**1, multiplier=4.184)
angstrom = FixedUnit('Å', m**1, multiplier=1e-10, latex_symbol='\\r{A}')

W = FixedUnit("W", J / s)
C = FixedUnit("C", A * s)
V = FixedUnit("V", J / C)
F = FixedUnit("F", C / V)
ohm = FixedUnit("Ω", V / A, latex_symbol='\\Omega')
Wb = FixedUnit("Wb", V * s)
T = FixedUnit("T", Wb / m**2)
H = FixedUnit("H", Wb / A)

__all__ = ['kg', 'm', 's', 'A', 'K', 'mol', 'cd', 'cm', 'g', 'mg', 'minute', 'h', 'N', 'Pa', 'atm', 'L', 'J', 'cal', 'angstrom', 'W', 'C', 'V', 'F', 'ohm', 'Wb', 'T', 'H']