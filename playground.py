import siunits as u
from siunits.predefined import *

# cc = u.unit.set("cc", cm ** 3)
# print(cc.depth, (cm**3).depth)
# print(cc + cm**3)
# print(cc * cm**3)
# print(cc == cm**3)

# print(0*kg == 0*A == 0)

A2 = u.unit.set("A_2", A)
# print(A * A2)
# print(A + A2)
# print(A == A2)

print(A - A2)
print(A - A2 == 0)
