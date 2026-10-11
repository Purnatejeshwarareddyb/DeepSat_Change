import os
from app.preprocessing.image_loader import load_image_bgr

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
MAX_DIMENSION = 12000


class ValidationResult:
    def __init__(self, is_valid, message="", metadata=None):
        self.is_valid = is_valid
        self.message = message
        self.metadata = metadata or {}


def validate_image(path):
    if not path or not os.path.exists(path):
        return ValidationResult(False, "The selected image does not exist.")

    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return ValidationResult(False, f"Unsupported format: {ext}")

    if os.path.getsize(path) == 0:
        return ValidationResult(False, "The selected image file is empty.")

    try:
        img = load_image_bgr(path)
    except Exception as exc:
        return ValidationResult(False, f"The image could not be opened or is corrupted: {exc}")

    h, w = img.shape[:2]
    if h == 0 or w == 0:
        return ValidationResult(False, "The image has invalid dimensions.")
    if h > MAX_DIMENSION or w > MAX_DIMENSION:
        return ValidationResult(False, "The image is extremely large and cannot be processed.")

    return ValidationResult(True, "Image is valid.", {"width": w, "height": h, "channels": img.shape[2]})


def validate_pair(before_path, after_path):
    r1 = validate_image(before_path)
    if not r1.is_valid:
        return r1
    r2 = validate_image(after_path)
    if not r2.is_valid:
        return r2
    if r1.metadata["width"] != r2.metadata["width"] or r1.metadata["height"] != r2.metadata["height"]:
        return ValidationResult(
            False,
            "The selected images have different dimensions. They can be resized automatically.",
            {"before": r1.metadata, "after": r2.metadata, "mismatch": True},
        )
    return ValidationResult(True, "Both images are valid and matching.", {"before": r1.metadata, "after": r2.metadata})
