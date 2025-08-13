import unittest
import numpy as np
from pymathnn.activations import Activations  # cambia 'your_module' con il nome del tuo file .py

class TestActivations(unittest.TestCase):
    
    def test_relu(self):
        x = np.array([-1, 0, 2])
        expected = np.array([0, 0, 2])
        result = Activations.relu(x)
        np.testing.assert_array_equal(result, expected)
    
    def test_sigmoid(self):
        x = np.array([0])
        expected = np.array([0.5])
        result = Activations.sigmoid(x)
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_tanh(self):
        x = np.array([0])
        expected = np.array([0.0])
        result = Activations.tanh(x)
        np.testing.assert_array_almost_equal(result, expected, decimal=6)
    
    def test_softmax(self):
        x = np.array([1, 2, 3])
        result = Activations.softmax(x)
        expected = np.exp(x - np.max(x)) / np.sum(np.exp(x - np.max(x)))
        np.testing.assert_array_almost_equal(result.flatten(), expected.flatten(), decimal=6)

if __name__ == '__main__':
    unittest.main()
