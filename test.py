# class A:
#     def __init__(self, value):
#         self.value = value
#
#     def __add__(self, other):
#         return _add(self, other)
#
#     def __sub__(self, other):
#         return _sub(self, other)
#
# class B(A):
#     def __init__(self, value):
#         super().__init__(value)
#
#     def __add__(self, other):
#         return _add(self, other)
#
#     def __sub__(self, other):
#         return _sub(self, other)
#
# from multipledispatch import dispatch
#
# # Assuming classes A and B are defined as in the provided code
#
# @dispatch(A, B)
# def _add(a, b):
#     return A(a.value + b.value)
#
# @dispatch(B, B)
# def _add(a, b):
#     # Implement specific logic for B if needed, else just reuse A's logic
#     return A(a.value + b.value)
#
# @dispatch(A, A)
# def _sub(a, b):
#     return A(a.value - b.value)
#
# @dispatch(B, B)
# def _sub(a, b):
#     # Implement specific logic for B if needed, else just reuse A's logic
#     return A(a.value - b.value)
#
# # Example usage remains the same
#
# # 사용 예시
# a = A(10)
# b = B(5)
#
# result_add = a + b  # A(15)
# result_sub = a - b  # A(5)
#
# print(result_add.value)  # 15
# print(result_sub.value)  # 5

from multipledispatch import dispatch

@dispatch(int, str)
def _add(a, b):
    print(a, b)
    return a + int(b)

if __name__ == "__main__":
    _add(3, "4")
    _add("4", 3)
