"""
🧮 Py_Math Matrix Library — NumPy-powered Matrix Operations

This package provides a versatile Matrix class for numerical computation, neural network preprocessing,
and mathematical utilities. It wraps NumPy arrays with additional features...

📦 Included modules:
- `matrix`: Core class for matrix algebra and utilities
- `activations`: Common neural activation functions (ReLU, Sigmoid, Tanh, Softmax)
- `deactivations`: Derivatives for use in backpropagation
💡 Key features:
- Matrix initialization via `zeros`, `random`, or `uniform`
- Arithmetic operations (add, multiply)
- Activation and deactivation methods
- Statistical tools (mean, norm, min/max, reshape, clip)
- Matrix utilities (transpose, flatten, norm of column)
🔍 Example usage:
```python
from py_math.matrix import Matrix
# Create a 3x4 matrix with random values from standard normal distribution
m1 = Matrix((3, 4), init='random')
# Apply ReLU activation to all elements
m1.activation("relu")
# Multiply by a scalar
m1 = m1.multiply(0.5)
# Print matrix summary
m1.summary()
# Reshape the matrix
m2 = m1.reshape((6, 2))
```
"""

import numpy as np
from .activations import Activations
from .deactivations import Deactivations

# Uso matrice come calcolo in numpy
# Shape inizializza la matrice (4,5) 4 righe 5 colonne
# Shape (4,5,6) indica 4 blocchi asse 0 ciascuno 5 righe e 6 valori

class Matrix:
    def __init__(self, shape = None, matrix: list = None, init='zeros' ):
        if shape is None and matrix is None:
            raise Exception(f"⚠️ Shape and Matrix is None. Evaluate shape or Matrix data")

        if shape is not None and ( not isinstance(shape, (tuple, list)) or not all(isinstance(x, int) and x > 0 for x in shape) ):
            raise ValueError(f"⚠️ La shape deve essere una tupla o lista di interi positivi, ricevuto: {shape}")

        if shape is not None and matrix is None:
            if init == 'zeros':
                self.matrix = np.zeros(shape)
            elif init == 'random':
                self.matrix = np.random.randn(*shape)
            elif init == 'xavier':
                stddev = np.sqrt(2 / (shape[0] + shape[1]))
                self.matrix = np.random.normal(0, stddev, size=(shape[0], shape[1]))
            elif init == 'uniform':
                self.matrix = np.random.uniform(-0.1, 0.1, size=shape)
            else:
                raise ValueError("Init method not supported")

        if matrix is not None:
            self.setting(matrix)
        else:
            self.shape = self.matrix.shape

        self.convert2D(self)

    def setting(self, matrix: list):
        self.matrix = np.array(matrix, dtype=np.float64)
        self.shape = self.matrix.shape

    def convert2D(self, x: 'Matrix') -> 'Matrix':
        if len(x.shape) == 1:
            x = x.reshape((x.shape[0],1)).transpose()
        self.matrix = x.matrix
        self.shape = x.shape
        return x

    def square(self) -> 'Matrix':
        result = Matrix(shape=self.shape)
        result.matrix = self.matrix ** 2
        return result

    def subtract(self, other: 'Matrix') -> 'Matrix':
        return self.add(other.multiply(-1))

    def add(self, other) -> 'Matrix':
        # Caso: somma con un'altra Matrix
        if isinstance(other, Matrix):
            if self.shape != other.shape:
                raise ValueError(f"Shape incompatibile: {self.shape} vs {other.shape}")
            result = self.copy()
            result.matrix += other.matrix
            return result

        # Caso: somma con scalare
        elif isinstance(other, (int, float)):
            result = self.copy()
            result.matrix += float(other)
            return result

        # Tipo non supportato
        else:
            raise TypeError(f"add() non supporta il tipo {type(other).__name__}")

    def to_numpy(self):
        return self.matrix

    def size(self):
        return self.matrix.size

    def sum(self, axis=None):
        if axis is None:
            return self.matrix.sum()
        else:
            data = self.matrix.sum(axis=axis)
            return Matrix(matrix=data)

    def multiply(self, scalar_or_matrix, mode = 'default') -> 'Matrix':
        if mode == 'elements':
            result = self.matrix * scalar_or_matrix.matrix
            return Matrix(matrix=result)

        #self.matrix = np.array(self.matrix)
        if isinstance(scalar_or_matrix, (int, float)):
            try:
                result = Matrix( shape=self.shape)
                result.matrix = self.matrix * float(scalar_or_matrix)
                return result
            except ValueError:
                raise TypeError(f"The scalar '{scalar_or_matrix}' can not converted to float.")

        elif isinstance(scalar_or_matrix, Matrix):
            try:
                result_np = self.matrix @ scalar_or_matrix.matrix
                result = Matrix( matrix=result_np )
                return result
            except Exception as e:
                raise ValueError(f"Shape incompatybility for multiply: {self.shape} @ {scalar_or_matrix.shape}: {e}")
        else:
            raise TypeError(f"Type not supported for multiply(): {type(scalar_or_matrix)}")

    def exp(self) -> 'Matrix':
        result = Matrix(self.shape)
        result.matrix = np.exp(self.matrix)
        return result

    def flatten(self) -> 'Matrix':
        flat_array = self.matrix.flatten()
        result = Matrix((flat_array.shape[0],))
        result.matrix = flat_array
        return result

    def transpose(self):
        transposed = self.matrix.T
        return Matrix(matrix=transposed)

    def max(self):
        num_rows = self.shape[0]

        if num_rows == 1:
            return self.matrix.max()
        else:
            matrix = Matrix((self.shape[0],1))
            matrix.matrix = np.array([max(row) for row in self.matrix])
            return matrix

    def min(self):
        return self.matrix.min()

    def mean(self):
        return self.matrix.mean()

    def norm(self):
        return np.linalg.norm(self.matrix)

    def clip(self, min_val, max_val):
        np.clip(self.matrix, min_val, max_val, out=self.matrix)

    def equals(self, m: 'Matrix') -> bool:
        if ( self.shape != m.shape ):
            return False

        return np.array_equal(self.matrix, m.matrix )

    def reshape(self, shape):
        if not isinstance(shape, (tuple, list)) or not all(isinstance(x, int) and x > 0 for x in shape):
            raise ValueError(f"⚠️ Error shape not a tuple or list of integer: {shape}")

        try:
            data = self.matrix.reshape(shape)
            return Matrix(matrix=data)
        except Exception as e:
            raise Exception("Error to reshape matrix: {self.shape} to {shape}")

    def norm_column(self, col_index: int) -> float:
        total = 0.0
        for i in range(self.shape[0]):
            val = self.matrix[i][col_index]
            total += val * val
        return total ** 0.5

    def activation(self, nome: str):
        # Mappa tra nome e funzione (puoi estendere)
        activations = {
            "relu": Activations.relu,
            "sigmoid": Activations.sigmoid,
            "tanh": Activations.tanh,
            "softmax": Activations.softmax
        }

        if nome not in activations:
            raise ValueError(f"⚠️ Funzione di attivazione '{nome}' non riconosciuta.")

        # Applica funzione elemento per elemento (eccetto softmax)
        if nome == "softmax":
            self.matrix = activations[nome](self.matrix)  # Assume che softmax sia già compatibile
        else:
            self.matrix = activations[nome](self.matrix) 
        return self

    def deactivation(self, nome: str):
        # Mappa tra nome e funzione derivata
        deactivations = {
            "relu": Deactivations.relu,
            "sigmoid": Deactivations.sigmoid,
            "tanh": Deactivations.tanh,
            "softmax": Deactivations.softmax
        }

        if nome not in deactivations:
            raise ValueError(f"⚠️ Funzione di deattivazione '{nome}' non riconosciuta.")

        if nome == "softmax":
            jacobian = deactivations[nome](self.matrix)  # Jacobiana di softmax
            self.matrix = jacobian @ np.squeeze(self.matrix, axis=0)
        else:
            self.matrix = deactivations[nome](self.matrix)
        return self

    def summary(self):
        print(f"📐 Shape: {self.shape}")
        print(f"🔢 Min: {np.min(self.matrix):.6f}, Max: {np.max(self.matrix):.6f}")
        print(f"📊 Mean: {np.mean(self.matrix):.6f}, Std: {np.std(self.matrix):.6f}")
        print(f"📐 Norm: {self.norm():.6f}")

    def copy(self):
        m = Matrix( self.shape )
        m.matrix = self.matrix.copy()
        return m

    def __str__(self):
        # Conversione in array NumPy per operazioni statistiche (se non lo è già)
        matrix_np = np.array(self.matrix)
        flat = matrix_np.flatten()

        # Calcolo anteprima
        total = len(flat)
        if total <= 6:
            preview = ", ".join(f"{val:.4f}" for val in flat)
        else:
            preview = ", ".join(f"{val:.4f}" for val in flat[:3]) + " ... " + ", ".join(f"{val:.4f}" for val in flat[-3:])


        return (
            f"📐 Shape: {self.shape}\n"
            f"🔢 Min: {np.min(matrix_np):.6f}, Max: {np.max(matrix_np):.6f}\n"
            f"📊 Mean: {np.mean(matrix_np):.6f}, Std: {np.std(matrix_np):.6f}\n"
            f"📐 Norm: {self.norm():.6f}\n"
            f"🔍 Preview: [{preview}]\n"
        )
