import unittest
import numpy as np
import matplotlib.pyplot as plt
from gradientvis.visualization.heatmap import plot_heatmap
from gradientvis.visualization.overlay import overlay_heatmap

class TestVisualization(unittest.TestCase):

    def setUp(self):
        self.activation_map = np.random.rand(224, 224)
        self.image = np.random.rand(224, 224, 3)

    def test_plot_heatmap(self):
        plot_heatmap(self.activation_map)
        # Check if plot appears (just testing if no error occurs)
        plt.close()

    def test_overlay_heatmap(self):
        overlay = overlay_heatmap(self.activation_map, self.image)
        self.assertEqual(overlay.shape, self.image.shape)

if __name__ == "__main__":
    unittest.main()
