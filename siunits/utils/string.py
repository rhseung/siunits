import re
from multipledispatch import dispatch
from fractions import Fraction

SMALL_SPACE = "\u2009"
MULTIPLY_SIGN = "\u22C5"
SMALL_SPACE_LATEX = r' \, '
MULTIPLY_SIGN_LATEX = r' \cdot '

subscripts = {
    '0': "\u2080",
    '1': "\u2081",
    '2': "\u2082",
    '3': "\u2083",
    '4': "\u2084",
    '5': "\u2085",
    '6': "\u2086",
    '7': "\u2087",
    '8': "\u2088",
    '9': "\u2089"
}

superscripts = {
    '0': "\u2070",
    '1': "\u00B9",
    '2': "\u00B2",
    '3': "\u00B3",
    '4': "\u2074",
    '5': "\u2075",
    '6': "\u2076",
    '7': "\u2077",
    '8': "\u2078",
    '9': "\u2079"
}

# @dispatch(int, int)
def pretty(n: int | float) -> str:
    return f"{n:.0f}" if float(n).is_integer() else f"{n}"

# @dispatch(str, (int, float), (int, float))
# def pretty(s: str, sub: int | float = None, sup: int | float = None) -> str:
#     subtext = ''
#     if sub is not None:
#         if isinstance(sub, float) and not sub.is_integer():
#             f = Fraction(f"{sub}")
#             subtext = ''.join(subscripts[d] for d in str(f.numerator)) + '/' + ''.join(subscripts[d] for d in str(f.denominator))
#         else:
#             subtext = ''.join(subscripts[d] for d in str(int(sub)))
#
#     supertext = ''
#     if sup is not None:
#         if isinstance(sup, float) and not sup.is_integer():
#             f = Fraction(f"{sup}")
#             supertext = ''.join(superscripts[d] for d in str(f.numerator)) + '/' + ''.join(superscripts[d] for d in str(f.denominator))
#         else:
#             supertext = ''.join(superscripts[d] for d in str(int(sup)))
#
#     return f"{s}{subtext}{supertext}"
#
# if __name__ == '__main__':
#     print(pretty('a', 178, 23))
#     print(pretty('a', 1.5, 2.5))
