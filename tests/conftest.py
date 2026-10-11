import os
import sys
import numpy as np
import cv2
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def synthetic_pair(tmp_path):
    before = np.random.randint(40, 200, (128, 128, 3), dtype=np.uint8)
    after = before.copy()
    after[30:70, 40:90] = 250

    mask = np.zeros((128, 128), dtype=np.uint8)
    mask[30:70, 40:90] = 255

    before_path = str(tmp_path / "before.png")
    after_path = str(tmp_path / "after.png")
    mask_path = str(tmp_path / "mask.png")
    cv2.imwrite(before_path, before)
    cv2.imwrite(after_path, after)
    cv2.imwrite(mask_path, mask)

    return {
        "before": before, "after": after, "mask": mask,
        "before_path": before_path, "after_path": after_path, "mask_path": mask_path,
    }


@pytest.fixture
def synthetic_dataset(tmp_path):
    root = tmp_path / "dataset"
    for split, n in [("train", 6), ("validation", 2), ("test", 2)]:
        for kind in ["before", "after", "mask"]:
            (root / split / kind).mkdir(parents=True, exist_ok=True)
        for i in range(n):
            before = np.random.randint(40, 200, (64, 64, 3), dtype=np.uint8)
            after = before.copy()
            mask = np.zeros((64, 64), dtype=np.uint8)
            after[10:30, 10:30] = 250
            mask[10:30, 10:30] = 255
            cv2.imwrite(str(root / split / "before" / f"{i:03d}.png"), before)
            cv2.imwrite(str(root / split / "after" / f"{i:03d}.png"), after)
            cv2.imwrite(str(root / split / "mask" / f"{i:03d}.png"), mask)
    return str(root)
