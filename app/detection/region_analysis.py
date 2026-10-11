import cv2
import numpy as np


def analyze_regions(binary_mask):
    mask_uint8 = (binary_mask * 255).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_uint8, connectivity=8)

    total_area = binary_mask.size
    regions = []
    for label_id in range(1, num_labels):
        x, y, w, h, area = stats[label_id]
        cx, cy = centroids[label_id]
        regions.append({
            "region_id": len(regions) + 1,
            "area": int(area),
            "width": int(w),
            "height": int(h),
            "bbox": [int(x), int(y), int(w), int(h)],
            "centroid": [round(float(cx), 1), round(float(cy), 1)],
            "relative_area": round((area / total_area) * 100, 3),
        })

    regions.sort(key=lambda r: r["area"], reverse=True)
    for i, r in enumerate(regions, start=1):
        r["region_id"] = i
    return regions
