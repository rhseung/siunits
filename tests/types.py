import pytest
from siunits.types import Unit, ComplexUnit, Dimension, DimensionMismatchError, ArithmeticDict

@pytest.fixture
def A():
    return Unit("A", Dimension(-3, -2, -1, 0, 1, 2, 3))

@pytest.fixture
def B():
    return Unit("B", Dimension(3, 2, 1, 0, -1, -2, -3))

@pytest.fixture
def C():
    return Unit("C", Dimension(-5, -4, -3, -2, -1, 0, 1))

@pytest.fixture
def A2():
    return Unit("A_2", Dimension(-3, -2, -1, 0, 1, 2, 3))

@pytest.fixture
def C_A(A):
    return ComplexUnit(ArithmeticDict({A: 1}))

@pytest.fixture
def C_B(B):
    return ComplexUnit(ArithmeticDict({B: 1}))

@pytest.fixture
def C_C(C):
    return ComplexUnit(ArithmeticDict({C: 1}))

@pytest.fixture
def C_A2(A2):
    return ComplexUnit(ArithmeticDict({A2: 1}))

@pytest.fixture
def C_1(A, B, C):
    return ComplexUnit(ArithmeticDict({A: 2, B: 3, C: 1}))

@pytest.fixture
def C_2(A, B, C):
    return ComplexUnit(ArithmeticDict({A: 3, B: 2, C: 1}))

# Addition Tests
def test_add_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A + A == ComplexUnit(ArithmeticDict({A: 1}), multiplier=2)
    assert B + B == ComplexUnit(ArithmeticDict({B: 1}), multiplier=2)
    assert C + C == ComplexUnit(ArithmeticDict({C: 1}), multiplier=2)
    with pytest.raises(DimensionMismatchError):
        A + B
    with pytest.raises(DimensionMismatchError):
        A + C
    with pytest.raises(DimensionMismatchError):
        B + C

def test_add_complex_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert C_A + C_A == ComplexUnit(ArithmeticDict({A: 1}), multiplier=2)
    assert C_B + C_B == ComplexUnit(ArithmeticDict({B: 1}), multiplier=2)
    assert C_C + C_C == ComplexUnit(ArithmeticDict({C: 1}), multiplier=2)
    with pytest.raises(DimensionMismatchError):
        C_A + C_B
    with pytest.raises(DimensionMismatchError):
        C_A + C_C
    with pytest.raises(DimensionMismatchError):
        C_B + C_C

    assert C_A + C_A2 == ComplexUnit(ArithmeticDict({A: 1}), multiplier=2)
    assert C_A2 + C_A == ComplexUnit(ArithmeticDict({A2: 1}), multiplier=2)

def test_add_unit_and_complex(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A + C_A == ComplexUnit(ArithmeticDict({A: 1}), multiplier=2)
    assert C_A + A == ComplexUnit(ArithmeticDict({A: 1}), multiplier=2)
    assert B + C_B == ComplexUnit(ArithmeticDict({B: 1}), multiplier=2)
    assert C_B + B == ComplexUnit(ArithmeticDict({B: 1}), multiplier=2)
    assert C + C_C == ComplexUnit(ArithmeticDict({C: 1}), multiplier=2)
    assert C_C + C == ComplexUnit(ArithmeticDict({C: 1}), multiplier=2)
    with pytest.raises(DimensionMismatchError):
        A + C_B
    with pytest.raises(DimensionMismatchError):
        B + C_C
    with pytest.raises(DimensionMismatchError):
        C + C_A

# Subtraction Tests
def test_sub_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A - A == 0
    assert B - B == 0
    assert C - C == 0
    with pytest.raises(DimensionMismatchError):
        A - B
    with pytest.raises(DimensionMismatchError):
        A - C
    with pytest.raises(DimensionMismatchError):
        B - C

def test_sub_complex_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert C_A - C_A == 0
    assert C_B - C_B == 0
    assert C_C - C_C == 0
    with pytest.raises(DimensionMismatchError):
        C_A - C_B
    with pytest.raises(DimensionMismatchError):
        C_A - C_C
    with pytest.raises(DimensionMismatchError):
        C_B - C_C

    assert C_A - C_A2 == 0

def test_sub_unit_and_complex(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A - C_A == 0
    assert C_A - A == 0
    assert B - C_B == 0
    assert C_B - B == 0
    assert C - C_C == 0
    assert C_C - C == 0
    with pytest.raises(DimensionMismatchError):
        A - C_B
    with pytest.raises(DimensionMismatchError):
        B - C_C
    with pytest.raises(DimensionMismatchError):
        C - C_A

# Multiplication Tests
def test_mul_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A * A == ComplexUnit(ArithmeticDict({A: 2}))
    assert B * B == ComplexUnit(ArithmeticDict({B: 2}))
    assert C * C == ComplexUnit(ArithmeticDict({C: 2}))
    assert A * B == ComplexUnit(ArithmeticDict({A: 1, B: 1}))
    assert A * C == ComplexUnit(ArithmeticDict({A: 1, C: 1}))
    assert B * C == ComplexUnit(ArithmeticDict({B: 1, C: 1}))

def test_mul_complex_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert C_A * C_A == ComplexUnit(ArithmeticDict({A: 2}))
    assert C_B * C_B == ComplexUnit(ArithmeticDict({B: 2}))
    assert C_C * C_C == ComplexUnit(ArithmeticDict({C: 2}))
    assert C_A * C_B == ComplexUnit(ArithmeticDict({A: 1, B: 1}))
    assert C_A * C_C == ComplexUnit(ArithmeticDict({A: 1, C: 1}))
    assert C_B * C_C == ComplexUnit(ArithmeticDict({B: 1, C: 1}))
    assert C_A * C_A2 == ComplexUnit(ArithmeticDict({A: 1, A2: 1}))

def test_mul_unit_and_complex(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A * C_A == ComplexUnit(ArithmeticDict({A: 2}))
    assert C_A * A == ComplexUnit(ArithmeticDict({A: 2}))
    assert B * C_B == ComplexUnit(ArithmeticDict({B: 2}))
    assert C_B * B == ComplexUnit(ArithmeticDict({B: 2}))
    assert C * C_C == ComplexUnit(ArithmeticDict({C: 2}))
    assert C_C * C == ComplexUnit(ArithmeticDict({C: 2}))
    assert A * C_B == ComplexUnit(ArithmeticDict({A: 1, B: 1}))
    assert B * C_A == ComplexUnit(ArithmeticDict({A: 1, B: 1}))
    assert C * C_A == ComplexUnit(ArithmeticDict({A: 1, C: 1}))

# Division Tests
def test_div_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A / A == ComplexUnit(ArithmeticDict())
    assert B / B == ComplexUnit(ArithmeticDict())
    assert C / C == ComplexUnit(ArithmeticDict())
    assert A / B == ComplexUnit(ArithmeticDict({A: 1, B: -1}))
    assert A / C == ComplexUnit(ArithmeticDict({A: 1, C: -1}))
    assert B / C == ComplexUnit(ArithmeticDict({B: 1, C: -1}))

def test_div_complex_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert C_A / C_A == ComplexUnit(ArithmeticDict())
    assert C_B / C_B == ComplexUnit(ArithmeticDict())
    assert C_C / C_C == ComplexUnit(ArithmeticDict())
    assert C_A / C_B == ComplexUnit(ArithmeticDict({A: 1, B: -1}))
    assert C_A / C_C == ComplexUnit(ArithmeticDict({A: 1, C: -1}))
    assert C_B / C_C == ComplexUnit(ArithmeticDict({B: 1, C: -1}))
    assert C_A / C_A2 == ComplexUnit(ArithmeticDict({A: 1, A2: -1}))

def test_div_unit_and_complex(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A / C_A == ComplexUnit(ArithmeticDict())
    assert C_A / A == ComplexUnit(ArithmeticDict())
    assert B / C_B == ComplexUnit(ArithmeticDict())
    assert C_B / B == ComplexUnit(ArithmeticDict())
    assert C / C_C == ComplexUnit(ArithmeticDict())
    assert C_C / C == ComplexUnit(ArithmeticDict())
    assert A / C_B == ComplexUnit(ArithmeticDict({A: 1, B: -1}))
    assert B / C_A == ComplexUnit(ArithmeticDict({B: 1, A: -1}))
    assert C / C_A == ComplexUnit(ArithmeticDict({C: 1, A: -1}))

# Power Tests
def test_pow_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert A ** 2 == ComplexUnit(ArithmeticDict({A: 2}))
    assert B ** 3 == ComplexUnit(ArithmeticDict({B: 3}))
    assert C ** 4 == ComplexUnit(ArithmeticDict({C: 4}))

def test_pow_complex_units(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert C_A ** 2 == ComplexUnit(ArithmeticDict({A: 2}))
    assert C_B ** 3 == ComplexUnit(ArithmeticDict({B: 3}))
    assert C_C ** 4 == ComplexUnit(ArithmeticDict({C: 4}))

# Complex operations with C_1 and C_2
def test_complex_operations(A, B, C, A2, C_A, C_B, C_C, C_A2, C_1, C_2):
    assert C_1 + C_1 == ComplexUnit(ArithmeticDict({A: 2, B: 3, C: 1}), multiplier=2)
    assert C_1 - C_1 == 0
    assert C_1 * C_2 == ComplexUnit(ArithmeticDict({A: 5, B: 5, C: 2}))
    assert C_1 / C_2 == ComplexUnit(ArithmeticDict({A: -1, B: 1}))
    assert C_1 ** 2 == ComplexUnit(ArithmeticDict({A: 4, B: 6, C: 2}))
    assert C_1 * C_2 * C_1 == ComplexUnit(ArithmeticDict({A: 7, B: 8, C: 3}))
    assert C_1 / (C_2 / C_1) == ComplexUnit(ArithmeticDict({A: 1, B: 4, C: 1}))
    assert (C_1 ** 2) ** 2 == ComplexUnit(ArithmeticDict({A: 8, B: 12, C: 4}))
