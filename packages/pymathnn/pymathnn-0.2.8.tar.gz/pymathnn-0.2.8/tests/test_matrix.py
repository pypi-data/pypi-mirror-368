import unittest
import numpy as np
from pymathnn.matrix import Matrix  # assuming your class is in matrix.py

class TestMatrix(unittest.TestCase):

    def setUp(self):
        # Matrice nota da usare in ogni test
        self.data = np.array([[1.0, 2.0], [3.0, 4.0]])
        self.data1 = np.array([[1.0, 2.0, 5], [3.0, 4.0, -1]])
        self.maxMatrix1 = Matrix((2,1))
        self.maxMatrix1.matrix = np.array([5,4])
        self.matrix = Matrix((2, 2))
        self.matrix1 = Matrix( (2, 3) )
        self.matrix.matrix = self.data.copy()
        self.matrix1.matrix = self.data1.copy()

    def test_copy(self):
        m = Matrix(matrix=[[1,4,5], [22,56,55]])
        copy = m.copy()
        self.assertEqual( m.matrix.tolist(), copy.matrix.tolist() )

    def test_initialize(self):
        m = Matrix( matrix=[1,4] )
        self.assertEqual( m.matrix.tolist(), [[1,4]] )

    def test_equal(self):
        copy = self.matrix.copy()
        false_eq = self.matrix1.equals(self.matrix)
        true_eq = self.matrix.equals(copy)
        self.assertFalse( false_eq )
        self.assertTrue( true_eq )

    def test_init_shape(self):
        m = Matrix(shape=(3, 4), init='zeros')
        m1 = Matrix(shape=(2,1), init='zeros')
        m2 = Matrix(shape=(2,), init='zeros')
        m3 = Matrix(matrix=[[0],[0]] )
        m4 = Matrix(matrix=[0,0] )
        self.assertEqual(m1.matrix.tolist(), [[0],[0]] )
        self.assertEqual(m2.matrix.tolist(), [[0,0]] )
        self.assertEqual(m3.shape , (2,1) )
        self.assertEqual(m4.shape , (1,2) )
        self.assertEqual(m.shape, (3, 4))
        self.assertTrue( np.all(m.matrix == 0))

    def test_init_data(self):
        m = Matrix(matrix = [[4.3,4]] )
        self.assertEqual(m.matrix.tolist(), [[4.3,4]])
        self.assertEqual(m.shape, (1,2) )

    def test_random_init(self):
        m = Matrix((2, 2), init='random')
        self.assertEqual(m.shape, (2, 2))
        self.assertIsInstance(m.matrix[0][0], float)

    def test_xavier_init(self):
        m = Matrix((2, 2), init='xavier')
        self.assertEqual(m.shape, (2, 2))
        self.assertIsInstance(m.matrix[0][0], float)

    def test_uniform_range(self):
        m = Matrix((2, 2), init='uniform')
        self.assertTrue(np.all(m.matrix >= -0.1))
        self.assertTrue(np.all(m.matrix <= 0.1))

    def test_add(self):
        m1 = Matrix((2, 2), init='zeros')
        m2 = Matrix((2, 2), init='uniform')
        result = m2.add(m1)
        self.assertEqual(result.shape, (2, 2))
        self.assertTrue( m2.equals(result) )

    def test_subtract(self):
        m1 = Matrix(matrix=[3,3])
        m2 = Matrix(matrix=[1,2])
        m3 = m1.subtract(m2)
        self.assertEqual( m3.matrix.tolist(), [[2.0,1.0]])
        
    def test_add_immutability(self):
        m1 = Matrix((2, 2), init='uniform')
        m2 = Matrix((2, 2), init='zeros')
        before = m1.copy()
        result = m1.add(m2)
        self.assertTrue(np.allclose(before.matrix, m1.matrix))  # m1 non deve cambiare

    def test_matrix_multiplication(self):
        m1 = Matrix(shape=(2, 3), init='uniform')
        m2 = Matrix(shape=(3, 4), init='uniform')
        result = m1.multiply(m2)
        r = m1.matrix @ m2.matrix
        self.assertEqual(result.shape, (2, 4))
        self.assertEqual(result.matrix.tolist(),  r.tolist() )
        m3 = Matrix(shape=(1,2), init='uniform')
        m4 = Matrix(shape=(2,4), init='uniform')
        r1m =  m3.multiply(m4)
        r1 = m3.matrix @ m4.matrix
        self.assertEqual(r1.shape, (1,4))
        self.assertEqual(r1.tolist(),  r1m.matrix.tolist() )

    def test_multiplication_elements(self):
        m1 = Matrix( matrix = [[3,3],[2,1]] )
        m2 = Matrix( matrix = [[1,-1],[2,11]] )
        m22 = Matrix( matrix = [[1,-1],[2,11],[1,2]] )
        m3 = m1.multiply(m2,mode='elements')
        with self.assertRaises(ValueError) as context:
            m4 = m1.multiply( m22, mode='elements')
        self.assertIn("operands could not", str(context.exception))
        self.assertEqual(m3.matrix.tolist(),[[3,-3],[4,11]] )

    def test_invalid_matrix_multiplication(self):
        m1 = Matrix(shape=(2, 3), init='uniform')
        m2 = Matrix(shape=(5, 4), init='uniform')  # shape incompatibile
        m3 = Matrix(shape=(5, ), init='uniform')

        with self.assertRaises(ValueError) as context:
            m1.multiply(m2)

        self.assertIn("Shape incompatybility", str(context.exception))
        
        with self.assertRaises(TypeError) as context1:
            m1.multiply([4,4])

        self.assertIn("Type not supported", str(context1.exception))

        with self.assertRaises(ValueError) as context2:
            m2.multiply( m3 )
        self.assertIn("Shape incompatybility", str(context2.exception))

    def test_exp_known_values(self):
        m = Matrix((1, 3))
        m.matrix = np.array([[-1, 0.0, 1.0]])
        result = m.exp()
        expected = np.exp(m.matrix) 
        self.assertEqual( result.matrix.tolist(), expected.tolist() )

    def test_multiply_scalar(self):
        result = self.matrix1.multiply(2)
        data = self.data1 * 2
        self.assertEqual( self.matrix1.shape,  result.shape )
        self.assertEqual( result.matrix.tolist() , data.tolist())
        m = Matrix(matrix=[3,1.1])
        res = m.multiply(4)
        self.assertEqual(res.matrix.tolist(), [[12,4.4]])

    def test_transpose(self):
        m = Matrix((3, 2), init='zeros')
        trans = m.transpose()
        self.assertEqual(trans.shape, (2, 3))

    def test_norm(self):
        m = Matrix((2, 2), init='zeros')
        self.assertEqual(m.norm(), 0.0)

    def test_reshape(self):
        m = Matrix(shape=(2, 2), init='zeros')
        result = m.reshape((1, 4))
        self.assertEqual(result.shape, (1, 4))
        m = Matrix(matrix=[1])
        self.assertEqual(m.shape, (1,1))
        r = m.reshape((1,1))
        self.assertEqual(m.shape, (1,1))
        self.assertEqual(r.shape, (1,1))

    def test_reshape_padding(self):
        m = Matrix((1, 2))
        m.matrix = np.array([[1.0, 2.0]])
        with self.assertRaises(Exception) as context:
            reshaped = m.reshape((2, 2))
        self.assertIn("Error to reshape", str(context.exception))
    
    def test_square(self):
        m = Matrix(matrix=[2,4])
        square = m.square()
        self.assertEqual(square.matrix.tolist(), [[4,16]])

    def test_reshape_truncation(self):
        m = Matrix((2, 2))
        m.matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
        with self.assertRaises(Exception) as context:
            reshaped = m.reshape((1, 2))
        self.assertIn("Error to reshape", str(context.exception))

    def test_clip(self):
        m = Matrix((2, 2), init='uniform')
        m.clip(-0.05, 0.05)
        self.assertTrue(np.all(m.matrix >= -0.05))
        self.assertTrue(np.all(m.matrix <= 0.05))

    def test_invalid_shape(self):
        with self.assertRaises(ValueError):
            Matrix((2, -1), init='zeros')

    def test_invalid_scalar(self):
        m = Matrix((2, 2), init='zeros')
        with self.assertRaises(TypeError):
            m.multiply("abc")

    def test_max_single_row(self):
        m = Matrix((1, 3))
        m.matrix = np.array([[1.0, 3.0, 2.0]])
        self.assertEqual(m.max(), 3.0)

    def test_max_multi_row(self):
        result = self.matrix1.max()
        self.assertTrue( result.equals( self.maxMatrix1) )

    def test_flatten_correctness(self):
        m = Matrix((2, 2))
        m.matrix = np.array([[1, 2], [3, 4]])
        flat = m.flatten()
        self.assertTrue(np.allclose(flat.matrix.flatten(), [1, 2, 3, 4]))

    def test_norm_column(self):
        m = Matrix((2, 1))
        m.matrix = np.array([[3.0], [4.0]])
        norm = m.norm_column(0)
        self.assertAlmostEqual(norm, 5.0)

    def test_str_output(self):
        m = Matrix((1, 3))
        output = str(m)
        self.assertTrue("Shape" in output and "Preview" in output)

    def test_activation_sigmoid(self):
        m = Matrix((2, 2))
        m.matrix = np.array([[0.0, 1.0], [-1.0, 2.0]])
        m.activation("sigmoid")
        expected = 1 / (1 + np.exp(-np.array([[0.0, 1.0], [-1.0, 2.0]])))
        self.assertTrue(np.allclose(m.matrix, expected, atol=1e-6))

    def test_deactivation_sigmoid(self):
        m = Matrix((2, 2))
        x = [[0.0, 1.0], [-1.0, 2.0]]
        m.matrix = np.array(x)
        m.activation("sigmoid")
        m.deactivation("sigmoid")
        sig = 1 / (1 + np.exp( -np.array(x)) )
        expected = sig * (1 - sig)
        self.assertEqual(m.matrix.tolist(), expected.tolist() )

    def test_activation_relu(self):
        m = Matrix((2, 2))
        m.matrix = np.array([[-1.0, 0.0], [2.0, -3.0]])
        m.activation("relu")
        expected = np.maximum(0, np.array([[-1.0, 0.0], [2.0, -3.0]]))
        self.assertTrue(np.allclose(m.matrix, expected))

    def test_deactivatio_relu(self):
        m = Matrix((2, 2))
        m.matrix = np.array([[-1.0, 0.0], [2.0, -3.0]])
        m.deactivation("relu")
        expected = np.array([[0, 0], [1, 0]])
        self.assertTrue(np.allclose(m.matrix, expected))

    def test_activation_tanh(self):
        m = Matrix((2, 2))
        m.matrix = np.array([[0.0, 1.0], [-1.0, 2.0]])
        m.activation("tanh")
        expected = np.tanh(np.array([[0.0, 1.0], [-1.0, 2.0]]))
        self.assertTrue(np.allclose(m.matrix, expected, atol=1e-6))

    def test_deactivation_tanh(self):
        m = Matrix((2, 2))
        m.matrix = np.array([[0.0, 1.0], [-1.0, 2.0]])
        x = m.copy()
        m.activation("tanh")
        x.deactivation("tanh")
        tanh_vals = np.array([[0.0, 1.0], [-1.0, 2.0]])
        expected = 1 - tanh_vals ** 2
        self.assertEqual( 
           [[round(val, 5) for val in row] for row in x.matrix.tolist()],
           [[round(val, 5) for val in row] for row in expected.tolist()]
        )

    def test_activation_softmax(self):
        m = Matrix((2, 3))
        m.matrix = np.array([[1.0, 2.0, 3.0],[-1.0, 12.0, 6.0]])
        m.activation("softmax")
        exp_vals = np.exp(m.matrix)
        expected = exp_vals / np.sum(exp_vals)
        self.assertTrue( m.matrix.tolist(), expected.tolist() )

    '''
    def test_deactivation_softmax(self):
        x = [[1.0, 2.0, 3.0],[1.0, 3.0, -1.0]]
        m = Matrix(matrix=x)
        m_x = m.copy()
        self.assertEqual( m.matrix.tolist(), m_x.matrix.tolist())
        m_x.deactivation("softmax")
        sm = np.exp( np.array(x) )
        sm = sm / np.sum(sm, axis=1, keepdims=True)
        expected = np.diag(sm[0]) - np.outer(sm[0], sm[0])
        print(m_x.matrix.tolist())
        self.assertEqual( 
           [[round(val, 5) for val in row] for row in m_x.matrix.tolist()],
           [[round(val, 5) for val in row] for row in expected.tolist()]
        )
    '''

if __name__ == '__main__':
    unittest.main()
