import cv2
import numpy as np


def build_overlay(base_rgb, binary_mask, color=(255, 0, 60), opacity=0.5):
    overlay = base_rgb.copy()
    colored = np.zeros_like(base_rgb)
    colored[binary_mask > 0] = color
    blended = cv2.addWeighted(colored, opacity, overlay, 1 - opacity, 0)
    result = overlay.copy()
    result[binary_mask > 0] = blended[binary_mask > 0]
    return result
