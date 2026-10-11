import json
import os
import tensorflow as tf
from app.models.unet import build_lightweight_unet, count_parameters
from app.models.losses import bce_dice_loss
from app.models.metrics import iou_metric, dice_metric
from app.utils.config import config, ROOT_DIR
from app.utils.logger import log

CUSTOM_OBJECTS = {
    "bce_dice_loss": bce_dice_loss(),
    "loss_fn": bce_dice_loss(),
    "iou_metric": iou_metric,
    "dice_metric": dice_metric,
}


class ModelManager:
    def __init__(self):
        self.model = None
        self.metadata = {}

    @property
    def models_dir(self):
        d = os.path.join(ROOT_DIR, "models")
        os.makedirs(d, exist_ok=True)
        return d

    def best_model_path(self):
        return os.path.join(self.models_dir, "best_model.keras")

    def latest_model_path(self):
        return os.path.join(self.models_dir, "latest_model.keras")

    def metadata_path(self):
        return os.path.join(self.models_dir, "model_metadata.json")

    def is_model_available(self):
        return os.path.exists(self.best_model_path()) or os.path.exists(self.latest_model_path())

    def build_new(self, image_size=256, in_channels=6):
        self.model = build_lightweight_unet(image_size, in_channels)
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=config.get("learning_rate", 0.001)),
            loss=bce_dice_loss(),
            metrics=[iou_metric, dice_metric, "accuracy"],
        )
        return self.model

    def load(self, path=None):
        path = path or (self.best_model_path() if os.path.exists(self.best_model_path()) else self.latest_model_path())
        if not os.path.exists(path):
            log.warning(f"No model found at {path}")
            return None
        self.model = tf.keras.models.load_model(path, custom_objects=CUSTOM_OBJECTS, compile=False)
        self.metadata = self._read_metadata()
        log.info(f"Model loaded successfully from {os.path.basename(path)}")
        return self.model

    def save(self, path, extra_metadata=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)
        if extra_metadata:
            self._write_metadata(extra_metadata)

    def _write_metadata(self, metadata):
        with open(self.metadata_path(), "w") as f:
            json.dump(metadata, f, indent=2)
        self.metadata = metadata

    def _read_metadata(self):
        if os.path.exists(self.metadata_path()):
            try:
                with open(self.metadata_path(), "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def summary_info(self):
        if self.model is None:
            return None
        total, trainable = count_parameters(self.model)
        info = {
            "model_name": self.model.name,
            "input_shape": str(self.model.input_shape),
            "total_parameters": total,
            "trainable_parameters": trainable,
        }
        info.update(self.metadata)
        return info


model_manager = ModelManager()
