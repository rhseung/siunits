import pytest
from copy import deepcopy
from siunits.utils import ArithmeticDict, Multitone

def test_arithmetic_dict_initialization():
    ad = ArithmeticDict()
    assert isinstance(ad, ArithmeticDict)

def test_arithmetic_dict_addition():
    ad1 = ArithmeticDict({'a': 1, 'b': 2})
    ad2 = ArithmeticDict({'b': 3, 'c': 4})
    result = ad1 + ad2
    expected = ArithmeticDict({'a': 1, 'b': 5, 'c': 4})
    assert result == expected

def test_arithmetic_dict_subtraction():
    ad1 = ArithmeticDict({'a': 5, 'b': 3})
    ad2 = ArithmeticDict({'b': 2, 'c': 1})
    result = ad1 - ad2
    expected = ArithmeticDict({'a': 5, 'b': 1, 'c': -1})
    assert result == expected

def test_arithmetic_dict_multiplication():
    ad1 = ArithmeticDict({'a': 2, 'b': 3})
    ad2 = ArithmeticDict({'b': 4, 'c': 5})
    result = ad1 * ad2
    expected = ArithmeticDict({'a': 0, 'b': 12, 'c': 0})  # Assuming default_factory is int, which initializes to 0
    assert result == expected

def test_arithmetic_dict_division():
    ad1 = ArithmeticDict({'a': 10, 'b': 20})
    ad2 = ArithmeticDict({'b': 2, 'c': 5})
    with pytest.raises(ZeroDivisionError):
        result = ad1 / ad2

def test_arithmetic_dict_division_no_zero():
    ad1 = ArithmeticDict({'a': 10, 'b': 20, 'c': 0})
    ad2 = ArithmeticDict({'a': 1, 'b': 2, 'c': 5, 'd': 1})  # Ensure no zero values for division
    result = ad1 / ad2
    expected = ArithmeticDict({'a': 10, 'b': 10, 'c': 0, 'd': 0})  # Assuming default_factory is int
    assert result == expected

def test_arithmetic_dict_floor_division():
    ad1 = ArithmeticDict({'a': 9, 'b': 20})
    ad2 = ArithmeticDict({'b': 2, 'c': 5})
    with pytest.raises(ZeroDivisionError):
        result = ad1 // ad2

def test_arithmetic_dict_floor_division_no_zero():
    ad1 = ArithmeticDict({'a': 9, 'b': 20, 'c': 0})
    ad2 = ArithmeticDict({'a': 2, 'b': 2, 'c': 5, 'd': 1})  # Ensure no zero values for division
    result = ad1 // ad2
    expected = ArithmeticDict({'a': 4, 'b': 10, 'c': 0, 'd': 0})  # Assuming default_factory is int
    assert result == expected

def test_arithmetic_dict_modulo():
    ad1 = ArithmeticDict({'a': 10, 'b': 21})
    ad2 = ArithmeticDict({'b': 2, 'c': 5})
    with pytest.raises(ZeroDivisionError):
        result = ad1 % ad2

def test_arithmetic_dict_modulo_no_zero():
    ad1 = ArithmeticDict({'a': 10, 'b': 21, 'c': 0})
    ad2 = ArithmeticDict({'a': 1, 'b': 2, 'c': 5, 'd': 1})
    result = ad1 % ad2
    expected = ArithmeticDict({'a': 0, 'b': 1, 'c': 0, 'd': 0})
    assert result == expected

def test_arithmetic_dict_power():
    ad1 = ArithmeticDict({'a': 2, 'b': 3})
    ad2 = ArithmeticDict({'b': 2, 'c': 3})
    result = ad1 ** ad2
    expected = ArithmeticDict({'a': 1, 'b': 9, 'c': 0})
    assert result == expected

def test_arithmetic_dict_or():
    ad1 = ArithmeticDict({'a': 0, 'b': 1})
    ad2 = ArithmeticDict({'b': 0, 'c': 1})
    result = ad1 | ad2
    expected = ArithmeticDict({'a': 0, 'b': 1, 'c': 1})
    assert result == expected

def test_arithmetic_dict_and():
    ad1 = ArithmeticDict({'a': 0, 'b': 1})
    ad2 = ArithmeticDict({'b': 0, 'c': 1})
    result = ad1 & ad2
    expected = ArithmeticDict({'b': 1})
    assert result == expected

def test_arithmetic_dict_unary_operations():
    ad = ArithmeticDict({'a': -2, 'b': 3})
    neg_result = -ad
    pos_result = +ad
    abs_result = abs(ad)
    round_result = round(ad, 1)
    floor_result = ad.__floor__()
    ceil_result = ad.__ceil__()
    assert neg_result == ArithmeticDict({'a': 2, 'b': -3})
    assert pos_result == ad
    assert abs_result == ArithmeticDict({'a': 2, 'b': 3})
    assert round_result == ad  # No change because values are integers
    assert floor_result == ad  # No change because values are integers
    assert ceil_result == ArithmeticDict({'a': -1, 'b': 4})  # Adjusting towards the higher integer

def test_arithmetic_dict_deepcopy():
    ad = ArithmeticDict({'a': 1, 'b': 2})
    ad_copy = deepcopy(ad)
    assert ad is not ad_copy
    assert ad == ad_copy

class TestClassA(metaclass=Multitone):
    def __init__(self, arg1, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2

class TestClassASub(TestClassA):
    pass

class TestClassB(metaclass=Multitone):
    def __init__(self, arg1, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2

def test_multitone_unique_instances_for_different_arguments():
    instance_a1 = TestClassA(1, 2)
    instance_a2 = TestClassA(1, 3)
    assert instance_a1 is not instance_a2

def test_multitone_same_instance_for_same_arguments():
    instance_a1 = TestClassA(1, 2)
    instance_a2 = TestClassA(1, 2)
    assert instance_a1 is instance_a2

def test_multitone_distinct_instances_across_classes():
    instance_a = TestClassA(1, 2)
    instance_b = TestClassB(1, 2)
    assert instance_a is not instance_b

# note: 같은 인자를 가져도 다른 클래스면 다른 인스턴스로 구분하게 해놨는데 이게 나중에 단위 구현 시 Unit, ComplexUnit 등의 관계에서 어떻게 될지는 봐야 알 듯.
def test_multitone_inheritance_distinct_instances():
    instance_a = TestClassA(1, 2)
    instance_a_sub = TestClassASub(1, 2)
    assert instance_a is not instance_a_sub
    assert isinstance(instance_a, TestClassA)
    assert isinstance(instance_a_sub, TestClassASub)

def test_multitone_argument_mutation():
    args = [1, 2]
    instance_a1 = TestClassA(*args)
    args[1] = 3  # Mutate the argument list
    instance_a2 = TestClassA(1, 2)  # Use original arguments
    assert instance_a1 is instance_a2
