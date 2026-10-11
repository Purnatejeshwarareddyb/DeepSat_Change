import numpy as np
import tensorflow as tf
from app.preprocessing.image_loader import load_image_rgb
from app.preprocessing.augmentation import augment_triplet
import cv2


def _load_triplet(before_path, after_path, mask_path, image_size):
    before = cv2.resize(load_image_rgb(before_path), (image_size, image_size), interpolation=cv2.INTER_AREA)
    after = cv2.resize(load_image_rgb(after_path), (image_size, image_size), interpolation=cv2.INTER_AREA)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    mask = cv2.resize(mask, (image_size, image_size), interpolation=cv2.INTER_NEAREST)
    mask = (mask > 127).astype(np.uint8) * 255
    return before, after, mask


def _to_tensor(before, after, mask):
    before_n = before.astype(np.float32) / 255.0
    after_n = after.astype(np.float32) / 255.0
    mask_n = (mask.astype(np.float32) / 255.0)[..., None]
    x = np.concatenate([before_n, after_n], axis=-1)
    return x, mask_n


def build_dataset(sample_list, dataset_manager, split, image_size=256, batch_size=4, augment=False, shuffle=True):
    def generator():
        ids = list(sample_list)
        if shuffle:
            np.random.shuffle(ids)
        for sample_id in ids:
            paths = dataset_manager.pair_paths(split, sample_id)
            if not all(k in paths for k in ("before", "after", "mask")):
                continue
            before, after, mask = _load_triplet(paths["before"], paths["after"], paths["mask"], image_size)
            if augment:
                before, after, mask = augment_triplet(before, after, mask)
            x, y = _to_tensor(before, after, mask)
            yield x, y

    output_signature = (
        tf.TensorSpec(shape=(image_size, image_size, 6), dtype=tf.float32),
        tf.TensorSpec(shape=(image_size, image_size, 1), dtype=tf.float32),
    )

    ds = tf.data.Dataset.from_generator(generator, output_signature=output_signature)
    if shuffle:
        ds = ds.shuffle(buffer_size=min(200, max(1, len(sample_list))))
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds
