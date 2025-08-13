import numpy as np

class Activations:
    @staticmethod
    def relu(x):
        return np.maximum(0, x)

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def tanh(x):
        return np.tanh(x)

    @staticmethod
    def softmax(x):
        e_x = np.exp(x - np.max(x))  # stabilizzazione numerica
        return e_x / np.sum(e_x, axis=-1, keepdims=True)
