import random
import cv2
import numpy as np


def augment_triplet(before, after, mask):
    if random.random() < 0.5:
        before = np.fliplr(before)
        after = np.fliplr(after)
        mask = np.fliplr(mask)

    if random.random() < 0.5:
        before = np.flipud(before)
        after = np.flipud(after)
        mask = np.flipud(mask)

    if random.random() < 0.5:
        k = random.choice([1, 2, 3])
        before = np.rot90(before, k)
        after = np.rot90(after, k)
        mask = np.rot90(mask, k)

    if random.random() < 0.5:
        alpha = random.uniform(0.85, 1.15)
        beta = random.uniform(-15, 15)
        before = np.clip(before.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)

    if random.random() < 0.5:
        alpha = random.uniform(0.85, 1.15)
        beta = random.uniform(-15, 15)
        after = np.clip(after.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)

    return np.ascontiguousarray(before), np.ascontiguousarray(after), np.ascontiguousarray(mask)
