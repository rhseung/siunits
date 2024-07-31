# siunits

SI 단위계를 파이썬에서 쉽게 사용할 수 있게 하는 라이브러리입니다. numpy를 지원합니다.

```shell
pip install siunits
```

## Features

```python
import siunits as u
from siunits.predefined import *

print(m) # 출력 결과: m
print(kg * m / s**2) # 출력 결과: kg ⋅ m / s^2

N_ = kg * m / s**2
print(N == N_) # 출력 결과: True
```

kg, m, s, A, K, mol, cd, cm, g, mg, minute, h, N, Pa, atm, L, J, cal, angstrom, W, C, V, F, ohm, Wb, T, H 등의 단위를 미리 정의해두었습니다. `siunits.predefined` 모듈을 사용하여 미리 정의된 단위를 사용할 수 있습니다.

```python
print(2 * kg) # 출력 결과: 2 kg
print(N * 3) # 출력 결과: 3 N
print(2 * kg + 3 * g) # 출력 결과: 2.003 kg
```

단위에는 연산자 오버로딩이 구현되어 있어, 단위 간의 연산이 가능합니다. 모든 단위들은 `int` 혹은 `float` 형의 숫자와 곱해질 수 있습니다.

```python
gravity = 9.81 * m / s**2
mass = 5 * kg

print(mass * gravity) # 출력 결과: 49.05 kg ⋅ m / s^2
print((mass * gravity).to(N)) # 출력 결과: 49.05 N
print((mass * gravity).to(ohm)) # 출력 결과: DimensionError
```

`to` 메소드를 사용하여 단위를 변환할 수 있습니다. 차원이 일치하지 않으면 `DimensionError`가 발생합니다.

```python
print(atm, atm.expand()) # 출력 결과: atm, 101325 Pa

expanded = ohm
print(expanded)
for _ in range(5):
    expanded = expanded.expand()
    print(expanded) 
    
# 출력 결과:
# Ω
# V / A
# J / A ⋅ C
# N ⋅ m / A ⋅ C
# kg ⋅ m^2 / A ⋅ C ⋅ s^2
# kg ⋅ m^2 / A^2 ⋅ s^3
```

`expand` 메소드를 사용하여 복합 단위를 구성하는 더 작은 단위로 분해할 수 있습니다.

```python
print(ohm)  # 출력 결과: Ω
print(ohm.si())  # 출력 결과: kg ⋅ m^2 / A^2 ⋅ s^3
```

`si` 메소드를 사용하여 단위를 SI 단위계의 가장 기본 단위인 kg, m, s, A, K, mol, cd로 변환할 수 있습니다.

```python
print([1, 2, 3] * m)
# 출력 결과: array([<Quantity 1 m> <Quantity 2 m> <Quantity 3 m>])

print((1.1, 1.2, 1.3) * m / s)
# 출력 결과: array([<Quantity 1.1 m / s> <Quantity 1.2 m / s> <Quantity 1.3 m / s>])

print(range(1, 7, 2) * T)
# 출력 결과: array([<Quantity 1 T> <Quantity 3 T> <Quantity 5 T>])

import numpy as np
print(np.arange(1, 5) * N)
# 출력 결과: array([<Quantity 1 N> <Quantity 2 N> <Quantity 3 N> <Quantity 4 N>])
```

`list[int | float]`, `tuple[int | float]`, `range`, `numpy.ndarray` 등의 자료형과 단위를 곱할 경우 `numpy.ndarray` 형의 객체가 반환됩니다.

> ```python
> (3*kg)**2 / (2*m)**3
> ```
> $\mathrm{ 1.125 \dfrac{kg^2}{m^3} }$
>
> ```python
> ohm
> ```
> $\mathrm{ Ω }$
>
> ```python
> ohm.si()
> ```
> $\mathrm{ \dfrac{kg \cdot m^2}{A^2 \cdot s^3} }$

IPython 커널 환경에서 사용할 경우, Rich Output을 지원합니다.

```python
import siunits as u

print(u.unit.find('T')) # 출력 결과: T
print(u.unit.find_all('T')) # 출력 결과: [T, T] 하나는 Tera, 다른 하나는 Tesla
# or
print(u.unit['T'])

# --------

AA = u.unit.set('AA', angstrom**2)
# or
u.unit['AA'] = angstrom**2
AA = u.unit['AA']
```

`unit.find`, `unit.find_all`, `unit.set` 메소드를 사용하여 단위를 찾거나 추가할 수 있습니다.
