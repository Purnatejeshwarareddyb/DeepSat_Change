import cv2
import numpy as np


def resize_to_match(before_bgr, after_bgr):
    h = min(before_bgr.shape[0], after_bgr.shape[0])
    w = min(before_bgr.shape[1], after_bgr.shape[1])
    before_r = cv2.resize(before_bgr, (w, h), interpolation=cv2.INTER_AREA)
    after_r = cv2.resize(after_bgr, (w, h), interpolation=cv2.INTER_AREA)
    return before_r, after_r


def preprocess_pair(before_bgr, after_bgr, image_size=256):
    before_rgb = cv2.cvtColor(before_bgr, cv2.COLOR_BGR2RGB)
    after_rgb = cv2.cvtColor(after_bgr, cv2.COLOR_BGR2RGB)

    before_r = cv2.resize(before_rgb, (image_size, image_size), interpolation=cv2.INTER_AREA)
    after_r = cv2.resize(after_rgb, (image_size, image_size), interpolation=cv2.INTER_AREA)

    before_n = before_r.astype(np.float32) / 255.0
    after_n = after_r.astype(np.float32) / 255.0

    tensor = np.concatenate([before_n, after_n], axis=-1)
    tensor = np.expand_dims(tensor, axis=0)
    return tensor, before_r, after_r
