import unittest
import numpy as np
import math
from pymathnn.deactivations import Deactivations
from pymathnn.activations import Activations

class TestDeactivations(unittest.TestCase):

    def test_sigmoid_derivative(self):
        x = np.array([0])
        expected = Activations.sigmoid(x) * (1 - Activations.sigmoid(x))
        result = Deactivations.sigmoid(Activations.sigmoid(x))
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_relu_derivative(self):
        self.assertEqual(Deactivations.relu(-1), 0)
        self.assertEqual(Deactivations.relu(0), 0)
        self.assertEqual(Deactivations.relu(2), 1)

    def test_tanh_derivative(self):
        x = np.array([[3,4,5],[4,1,-4]])
        expected = np.array([[math.tanh(a) for a in row] for row in x])
        expected = 1 - expected ** 2
        result = Deactivations.tanh(x)
        self.assertEqual(result.any(), expected.any() )

    def test_softmax_derivative(self):
        x = np.array([1.0, 2.0, 3.0])
        sm = Activations.softmax(x)
        result = Deactivations.softmax(x)
        
        # Check dimensions of Jacobian
        self.assertEqual(len(result), len(x))
        self.assertEqual(len(result[0]), len(x))
        
        # Check diagonal elements: sm[i] * (1 - sm[i])
        for i in range(len(x)):
            self.assertAlmostEqual(result[i][i], x[i] * (1 - x[i]), places=6)
        
        # Check off-diagonal elements: -sm[i] * sm[j]
        for i in range(len(x)):
            for j in range(len(x)):
                if i != j:
                    self.assertAlmostEqual(result[i][j], -x[i] * x[j], places=6)

if __name__ == '__main__':
    unittest.main(verbosity=2)
