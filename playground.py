import siunits as u
from siunits.utils.types import ArithmeticDict
from sortedcontainers import SortedDict

u1 = u.cm.to(u.m)
print(u1.multiplier)
print(str(u1))
