import os

IMG_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def _list_ids(folder):
    if not os.path.isdir(folder):
        return set()
    ids = set()
    for fname in os.listdir(folder):
        name, ext = os.path.splitext(fname)
        if ext.lower() in IMG_EXTENSIONS:
            ids.add(name)
    return ids


def validate_split(split_dir):
    before_dir = os.path.join(split_dir, "before")
    after_dir = os.path.join(split_dir, "after")
    mask_dir = os.path.join(split_dir, "mask")

    before_ids = _list_ids(before_dir)
    after_ids = _list_ids(after_dir)
    mask_ids = _list_ids(mask_dir)

    matching = before_ids & after_ids & mask_ids
    missing_before = after_ids - before_ids
    missing_after = before_ids - after_ids
    missing_mask = (before_ids & after_ids) - mask_ids

    return {
        "before_count": len(before_ids),
        "after_count": len(after_ids),
        "mask_count": len(mask_ids),
        "matching_pairs": len(matching),
        "missing_before": len(missing_before),
        "missing_after": len(missing_after),
        "missing_mask": len(missing_mask),
        "matching_ids": sorted(matching),
        "valid": len(matching) > 0,
    }


def validate_dataset(dataset_root):
    report = {}
    for split in ["train", "validation", "test"]:
        split_dir = os.path.join(dataset_root, split)
        report[split] = validate_split(split_dir)
    report["overall_valid"] = any(report[s]["valid"] for s in ["train", "validation", "test"])
    return report
