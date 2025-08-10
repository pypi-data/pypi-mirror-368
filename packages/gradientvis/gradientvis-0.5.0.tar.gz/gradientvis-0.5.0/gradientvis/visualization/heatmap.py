import numpy as np
import matplotlib.pyplot as plt
import cv2

def plot_heatmap(activation_map, colormap=cv2.COLORMAP_JET):
    activation_map = (activation_map - activation_map.min()) / (activation_map.max() - activation_map.min())
    heatmap = cv2.applyColorMap(np.uint8(255 * activation_map), colormap)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    plt.imshow(heatmap)
    plt.axis("off")
    plt.show()
