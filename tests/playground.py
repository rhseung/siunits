import siunits as u

C = u.FixedUnit('C', u.A * u.s)
F = u.FixedUnit('F', C ** 1, multiplier=96500)

print(u.atm.multiplier)
print(u.atm.expand())
print(u.atm.expand().expand(), u.Pa.expand(), sep=' | ')
