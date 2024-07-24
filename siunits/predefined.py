from siunits.unit import Unit, FixedUnit
from siunits.dimension import Dimension

kg = Unit('kg', Dimension(mass=1))
m = Unit('m', Dimension(length=1))
s = Unit('s', Dimension(time=1))
A = Unit('A', Dimension(current=1))
K = Unit('K', Dimension(temperature=1))
mol = Unit('mol', Dimension(amount=1))
cd = Unit('cd', Dimension(intensity=1))

cm = FixedUnit('cm', m**1, multiplier=1e-2)
minute = FixedUnit('min', s**1, multiplier=60)
N = FixedUnit('N', kg * m / s**2)
Pa = FixedUnit('Pa', N / m**2)
atm = FixedUnit('atm', Pa**1, multiplier=101325)
J = FixedUnit('J', N * m)
