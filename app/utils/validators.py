def validate_image_size(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False, "Image size must be an integer."
    if value < 64 or value > 1024:
        return False, "Image size must be between 64 and 1024."
    if value % 16 != 0:
        return False, "Image size should be a multiple of 16 for the U-Net encoder/decoder to align."
    return True, ""


def validate_batch_size(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False, "Batch size must be an integer."
    if value not in (1, 2, 4, 8, 16, 32):
        return False, "Recommended batch sizes for 8 GB RAM / CPU are 1, 2, 4, 8, 16, or 32."
    return True, ""


def validate_epochs(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False, "Epochs must be an integer."
    if value < 1 or value > 1000:
        return False, "Epochs must be between 1 and 1000."
    return True, ""


def validate_learning_rate(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return False, "Learning rate must be a number."
    if value <= 0 or value > 1:
        return False, "Learning rate must be between 0 and 1."
    return True, ""


def validate_threshold(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return False, "Threshold must be a number."
    if value < 0.1 or value > 0.9:
        return False, "Threshold must be between 0.10 and 0.90."
    return True, ""


def validate_min_region_size(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False, "Minimum region size must be an integer."
    if value < 1:
        return False, "Minimum region size must be at least 1 pixel."
    return True, ""


def validate_folder_path(path):
    import os
    if not path:
        return False, "Path cannot be empty."
    if not os.path.isdir(path):
        return False, f"The folder does not exist: {path}"
    return True, ""
