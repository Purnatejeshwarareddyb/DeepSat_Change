import numpy as np
from app.utils.helpers import severity_label


def compute_change_stats(binary_mask):
    total_pixels = int(binary_mask.size)
    changed_pixels = int(np.sum(binary_mask > 0))
    change_percent = (changed_pixels / total_pixels) * 100 if total_pixels else 0.0
    return {
        "total_pixels": total_pixels,
        "changed_pixels": changed_pixels,
        "change_percent": round(change_percent, 2),
        "severity": severity_label(change_percent),
    }
