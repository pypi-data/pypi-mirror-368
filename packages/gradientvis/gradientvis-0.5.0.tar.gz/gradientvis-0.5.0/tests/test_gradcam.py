import torch
import unittest
from gradientvis.methods.gradcam import GradCAM
from gradientvis.utils.preprocessing import preprocess_image

class TestGradCAM(unittest.TestCase):
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

    def test_gradcam_output(self):
        gradcam = GradCAM(self.model, self.model[2])
        cam = gradcam.generate(self.image, class_idx=0)
        self.assertEqual(cam.shape, (self.image.shape[2], self.image.shape[3]))

if __name__ == "__main__":
    unittest.main()
