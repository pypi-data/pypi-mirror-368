## Installation

```
pip install pymathnn
```

## Utilization

Simple examples of user:

```
from pymathnn import Matrix

m1 = Matrix((3, 3), init='random')
m2 = Matrix((3, 3), init='uniform')

# Sum matrix
m3 = m1.add(m2)

# Product With Scalar
m4 = m1.multiply(2.5)

# Matrix Traspose
mt = m1.transpose()

# Statistics
print(m1.mean())
print(m1.norm())
m1.summary()

# Activation
m1 = Matrix((4,4))
print(m1)
m1.activation('relu')
print(m1)
```
