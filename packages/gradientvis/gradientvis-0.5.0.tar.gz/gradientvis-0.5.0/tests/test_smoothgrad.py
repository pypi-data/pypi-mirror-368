import torch
import unittest
from gradientvis.methods.smoothgrad import SmoothGrad
from gradientvis.utils.preprocessing import preprocess_image

class TestSmoothGrad(unittest.TestCase):
    def setUp(self):
        self.model = torch.nn.Sequential(
            torch.nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU()
        )
        self.model.eval()
        self.image = preprocess_image("test_image.jpg")

    def test_smoothgrad_output(self):
        smoothgrad = SmoothGrad(self.model)
        grad = smoothgrad.generate(self.image, class_idx=0)
        self.assertEqual(grad.shape, (3, self.image.shape[2], self.image.shape[3]))

if __name__ == "__main__":
    unittest.main()
