import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_PATH = os.path.join(ROOT_DIR, "config", "settings.json")
DATASETS_PATH = os.path.join(ROOT_DIR, "config", "datasets.json")

DEFAULT_SETTINGS = {
    "image_size": 256,
    "batch_size": 4,
    "epochs": 20,
    "learning_rate": 0.001,
    "change_threshold": 0.5,
    "min_region_size": 100,
    "model_path": "models/best_model.keras",
    "dataset_path": "dataset",
    "output_path": "results",
    "animation_speed": 250,
}


class Config:
    def __init__(self):
        self._settings = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    data = json.load(f)
                self._settings.update(data)
            except (json.JSONDecodeError, OSError):
                pass
        else:
            self.save()

    def save(self):
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w") as f:
            json.dump(self._settings, f, indent=2)

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value
        self.save()

    def all(self):
        return dict(self._settings)

    def abs_path(self, key):
        p = self._settings.get(key, "")
        return p if os.path.isabs(p) else os.path.join(ROOT_DIR, p)

    def load_datasets_registry(self):
        if os.path.exists(DATASETS_PATH):
            try:
                with open(DATASETS_PATH, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {"available_datasets": []}
        return {"available_datasets": []}


config = Config()
