import os
import cv2
import numpy as np


def load_image_bgr(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not decode image: {path}")
    return img


def load_image_rgb(path):
    img = load_image_bgr(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def get_metadata(path):
    img = load_image_bgr(path)
    h, w, c = img.shape
    return {
        "filename": os.path.basename(path),
        "width": w,
        "height": h,
        "channels": c,
        "file_size": os.path.getsize(path),
        "format": os.path.splitext(path)[1].replace(".", "").upper(),
    }
