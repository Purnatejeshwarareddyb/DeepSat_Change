import cv2
import numpy as np
from scipy import ndimage


def threshold_mask(prob_map, threshold=0.5):
    return (prob_map >= threshold).astype(np.uint8)


def morphological_clean(binary_mask, kernel_size=3):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    opened = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    return closed


def remove_small_objects(binary_mask, min_size=100):
    labeled, num = ndimage.label(binary_mask)
    if num == 0:
        return binary_mask
    sizes = ndimage.sum(binary_mask, labeled, range(1, num + 1))
    cleaned = np.zeros_like(binary_mask)
    for i, size in enumerate(sizes, start=1):
        if size >= min_size:
            cleaned[labeled == i] = 1
    return cleaned.astype(np.uint8)


def clean_mask(prob_map, threshold=0.5, min_size=100, kernel_size=3):
    binary = threshold_mask(prob_map, threshold)
    binary = morphological_clean(binary, kernel_size)
    binary = remove_small_objects(binary, min_size)
    return binary
