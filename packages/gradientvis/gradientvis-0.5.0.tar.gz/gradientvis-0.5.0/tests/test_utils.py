import unittest
import numpy as np
from gradientvis.utils.postprocessing import normalize_map

class TestUtils(unittest.TestCase):

    def test_normalize_map(self):
        activation_map = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.float32)
        normalized_map = normalize_map(activation_map)
        self.assertTrue(np.all(normalized_map >= 0) and np.all(normalized_map <= 1))
        self.assertEqual(normalized_map.shape, activation_map.shape)

if __name__ == "__main__":
    unittest.main()
