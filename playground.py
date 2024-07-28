import siunits as u
from siunits.predefined import *

Mg = u.unit.set('Mg', 1e6 * g)

print(kg + g, kg + 2*Mg)
print(2*kg + 3*g)
print(2 * g + 3 * Mg) # 3000002 g
print(2 * kg + 3 * g)