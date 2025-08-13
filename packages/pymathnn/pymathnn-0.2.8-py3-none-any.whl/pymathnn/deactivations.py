import math
import numpy as np
from .activations import Activations

class Deactivations:
    @staticmethod
    def sigmoid(x):
        sx = x
        return sx * (1 - sx)

    @staticmethod
    def relu(x):
        return np.where(x > 0, 1, 0)

    @staticmethod
    def tanh(x):
        tx = x #Activations.tanh(x)
        return 1 - tx ** 2

    @staticmethod
    def softmax(x):
        # Derivata Softmax → matrice Jacobiana
        # Torna la Jacobiana (lista di liste)
        sm = x #Activations.softmax(vettore)
        n = len(sm)
        jacobiana = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    jacobiana[i][j] = sm[i] * (1 - sm[i])
                else:
                    jacobiana[i][j] = -sm[i] * sm[j]

        return np.array(jacobiana)
