import torch
import numpy as np

class SmoothGrad:
    def __init__(self, model, stdev=0.15, num_samples=50):
        self.model = model
        self.stdev = stdev
        self.num_samples = num_samples

    def generate(self, input_image, class_idx):
        self.model.zero_grad()
        input_image = input_image.clone().detach()
        gradients = torch.zeros_like(input_image)

        for _ in range(self.num_samples):
            noise = torch.randn_like(input_image) * self.stdev
            noisy_input = input_image + noise
            noisy_input.requires_grad = True

            output = self.model(noisy_input)
            score = output[:, class_idx]
            score.backward()

            gradients += noisy_input.grad

        avg_gradients = gradients / self.num_samples
        return avg_gradients.squeeze().cpu().numpy()
