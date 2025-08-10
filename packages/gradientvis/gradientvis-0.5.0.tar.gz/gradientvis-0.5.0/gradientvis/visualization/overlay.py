import numpy as np
import cv2

def overlay_heatmap(heatmap, image, alpha=0.5):
    heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    overlay = cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)
    return overlay
