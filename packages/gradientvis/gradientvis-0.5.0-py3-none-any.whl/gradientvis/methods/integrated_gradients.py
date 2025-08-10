import torch
import numpy as np

class IntegratedGradients:
    def __init__(self, model, steps=50, baseline=None):
        self.model = model
        self.steps = steps
        self.baseline = baseline

    def interpolate_images(self, input_image):
        baseline = self.baseline if self.baseline is not None else torch.zeros_like(input_image)
        alphas = torch.linspace(0, 1, self.steps).view(-1, 1, 1, 1).to(input_image.device)
        return baseline + alphas * (input_image - baseline)

    def generate(self, input_image, class_idx):
        self.model.zero_grad()
        input_image.requires_grad = True

        interpolated_images = self.interpolate_images(input_image)
        gradients = torch.zeros_like(input_image)

        for img in interpolated_images:
            img = img.unsqueeze(0)
            output = self.model(img)
            score = output[:, class_idx]
            score.backward()
            gradients += img.grad

        avg_gradients = gradients / self.steps
        integrated_gradients = (input_image - self.baseline) * avg_gradients
        return integrated_gradients.squeeze().cpu().numpy()
