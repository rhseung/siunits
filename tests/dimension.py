import pytest
from siunits.dimension import Dimension

def test_dimension_initialization():
    dim = Dimension(length=1, mass=1, time=1, current=1, temperature=1)
    assert dim.length == 1
    assert dim.mass == 1
    assert dim.time == 1
    assert dim.current == 1
    assert dim.temperature == 1
    assert dim.amount == 0
    assert dim.intensity == 0

def test_dimension_addition():
    dim1 = Dimension(length=1, mass=2, time=3, current=4, temperature=5, amount=6, intensity=7)
    dim2 = Dimension(length=1, mass=1, time=1, current=1, temperature=1, amount=1, intensity=1)
    result = dim1 + dim2
    assert result == Dimension(length=2, mass=3, time=4, current=5, temperature=6, amount=7, intensity=8)

def test_dimension_subtraction():
    dim1 = Dimension(length=5, mass=4, time=3, current=2, temperature=1, amount=0, intensity=-1)
    dim2 = Dimension(length=1, mass=1, time=1, current=1, temperature=1, amount=1, intensity=1)
    result = dim1 - dim2
    assert result == Dimension(length=4, mass=3, time=2, current=1, temperature=0, amount=-1, intensity=-2)

def test_dimension_multiplication():
    dim1 = Dimension(length=2, mass=3, time=4, current=5, temperature=6, amount=7, intensity=8)
    dim2 = Dimension(length=1, mass=2, time=3, current=4, temperature=5, amount=6, intensity=7)
    result = dim1 * dim2
    assert result == Dimension(length=2, mass=6, time=12, current=20, temperature=30, amount=42, intensity=56)

def test_dimension_scalar_multiplication():
    dim = Dimension(length=2, mass=3, time=4, current=5, temperature=6, amount=7, intensity=8)
    scalar = 2
    result = dim * scalar
    assert result == Dimension(length=4, mass=6, time=8, current=10, temperature=12, amount=14, intensity=16)

def test_dimension_division():
    dim1 = Dimension(length=10, mass=20, time=30, current=40, temperature=50, amount=60, intensity=70)
    dim2 = Dimension(length=2, mass=4, time=5, current=8, temperature=10, amount=12, intensity=14)
    result = dim1 / dim2
    assert result == Dimension(length=5, mass=5, time=6, current=5, temperature=5, amount=5, intensity=5)

def test_dimension_scalar_division():
    dim = Dimension(length=10, mass=20, time=30, current=40, temperature=50, amount=60, intensity=70)
    scalar = 2
    result = dim / scalar
    assert result == Dimension(length=5, mass=10, time=15, current=20, temperature=25, amount=30, intensity=35)
