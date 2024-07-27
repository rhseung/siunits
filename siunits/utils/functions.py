from functools import reduce, wraps

def product(iterable, initial=1):
    return reduce(lambda x, y: x * y, iterable, initial)

def reverse_f(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args[::-1], **kwargs)
    return wrapper

# def commutative(cls):
#     # 오버로딩된 이항 연산자들을 정의
#     binary_operators = [
#         '__add__', '__sub__', '__mul__', '__matmul__', '__truediv__', '__floordiv__',
#         '__mod__', '__divmod__', '__pow__', '__lshift__', '__rshift__', '__and__',
#         '__xor__', '__or__'
#     ]
#
#     # 각 연산자에 대해 역-연산자 설정
#     for op in binary_operators:
#         reverse_op = '__r' + op[2:]  # '__add__' -> '__radd__' 변환
#         if hasattr(cls, op):
#             original_method = getattr(cls, op)
#
#             @wraps(original_method)
#             def method(self, other):
#                 print(cls, self, other, original_method)
#                 return original_method(other, self)
#
#             setattr(cls, reverse_op, method)
#
#     return cls

__all__ = ['product', 'reverse_f']
