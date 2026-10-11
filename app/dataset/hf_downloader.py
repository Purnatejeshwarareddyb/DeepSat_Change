import os
import numpy as np
from PIL import Image
from app.utils.config import config
from app.utils.helpers import ensure_dir
from app.utils.logger import log

BEFORE_KEYS = ["image1", "before", "A", "image_before", "imageA", "before_image"]
AFTER_KEYS = ["image2", "after", "B", "image_after", "imageB", "after_image"]
MASK_KEYS = ["mask", "label", "change_mask"]


class HFDownloadError(Exception):
    pass


def _first_present(example, keys):
    for key in keys:
        if key in example and example[key] is not None:
            return example[key]
    return None


def _save_image(pil_img, path, max_side):
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    w, h = pil_img.size
    scale = max_side / max(w, h)
    if scale < 1.0:
        pil_img = pil_img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BILINEAR)
    pil_img.save(path)


def _save_mask(pil_img, path, max_side):
    if pil_img.mode != "L":
        pil_img = pil_img.convert("L")
    arr = np.array(pil_img)
    if arr.max() <= 1:
        arr = (arr * 255).astype(np.uint8)
    else:
        arr = (arr > 0).astype(np.uint8) * 255
    out = Image.fromarray(arr)
    w, h = out.size
    scale = max_side / max(w, h)
    if scale < 1.0:
        out = out.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)
    out.save(path)


def download_via_huggingface(dataset_entry, progress_callback=None, stop_flag=None,
                              max_side=256, val_every_n=7,
                              max_train=None, max_val=None, max_test=None):
    try:
        from datasets import load_dataset, get_dataset_split_names
    except ImportError:
        raise HFDownloadError(
            "The 'datasets' package is not installed. Run: pip install -r requirements.txt"
        )

    max_train = max_train if max_train is not None else config.get("max_train_samples", 600)
    max_val = max_val if max_val is not None else config.get("max_val_samples", 150)
    max_test = max_test if max_test is not None else config.get("max_test_samples", 150)

    dataset_id = dataset_entry.get("huggingface_dataset_id")
    if not dataset_id:
        raise HFDownloadError("No Hugging Face dataset id is configured for this entry.")

    try:
        available_splits = set(get_dataset_split_names(dataset_id))
    except Exception:
        available_splits = {"train", "test"}

    has_val_split = bool({"validation", "val"} & available_splits)
    val_split_name = "validation" if "validation" in available_splits else "val"

    dataset_root = config.abs_path("dataset_path")
    counts = {"train": 0, "validation": 0, "test": 0}
    limits = {"train": max_train, "validation": max_val, "test": max_test}

    plan = [("train", "train")]
    if has_val_split:
        plan.append((val_split_name, "validation"))
    if "test" in available_splits:
        plan.append(("test", "test"))

    for hf_split, local_split_fixed in plan:
        try:
            stream = load_dataset(dataset_id, split=hf_split, streaming=True)
        except Exception as exc:
            raise HFDownloadError(
                f"Could not open the '{hf_split}' split of '{dataset_id}' from Hugging Face. "
                f"Check your internet connection and try again. Details: {exc}"
            )

        for i, example in enumerate(stream):
            if stop_flag is not None and stop_flag.is_set():
                raise HFDownloadError("Download cancelled.")

            if local_split_fixed == "train" and not has_val_split:
                local_split = "validation" if (i % val_every_n == 0) else "train"
            else:
                local_split = local_split_fixed

            if counts[local_split] >= limits[local_split]:
                if all(counts[s] >= limits[s] for s in limits):
                    break
                continue

            before_img = _first_present(example, BEFORE_KEYS)
            after_img = _first_present(example, AFTER_KEYS)
            mask_img = _first_present(example, MASK_KEYS)
            if before_img is None or after_img is None or mask_img is None:
                continue

            before_dir = ensure_dir(os.path.join(dataset_root, local_split, "before"))
            after_dir = ensure_dir(os.path.join(dataset_root, local_split, "after"))
            mask_dir = ensure_dir(os.path.join(dataset_root, local_split, "mask"))

            stem = f"{counts[local_split]:05d}"
            _save_image(before_img, os.path.join(before_dir, f"{stem}.png"), max_side)
            _save_image(after_img, os.path.join(after_dir, f"{stem}.png"), max_side)
            _save_mask(mask_img, os.path.join(mask_dir, f"{stem}.png"), max_side)

            counts[local_split] += 1
            if progress_callback and i % 3 == 0:
                progress_callback(local_split, counts[local_split])

    total = sum(counts.values())
    if total == 0:
        raise HFDownloadError(
            "No usable image triplets were found in this dataset. "
            "The dataset schema may have changed; please report this or use USE LOCAL DATASET instead."
        )

    log.info("Hugging Face dataset download and organization completed")
    return counts
