import os
from app.utils.config import config, ROOT_DIR
from app.dataset.dataset_validator import validate_dataset


class DatasetManager:
    def dataset_root(self):
        return config.abs_path("dataset_path")

    def is_dataset_ready(self):
        report = validate_dataset(self.dataset_root())
        return report.get("overall_valid", False)

    def validation_report(self):
        return validate_dataset(self.dataset_root())

    def set_local_dataset(self, folder_path):
        config.set("dataset_path", folder_path if os.path.isabs(folder_path) else os.path.relpath(folder_path, ROOT_DIR))
        return self.validation_report()

    def matching_pairs(self, split="train"):
        report = self.validation_report()
        return report.get(split, {}).get("matching_ids", [])

    def pair_paths(self, split, sample_id):
        root = self.dataset_root()
        exts = [".png", ".jpg", ".jpeg", ".tif", ".tiff"]
        result = {}
        for kind in ["before", "after", "mask"]:
            folder = os.path.join(root, split, kind)
            for ext in exts:
                candidate = os.path.join(folder, sample_id + ext)
                if os.path.exists(candidate):
                    result[kind] = candidate
                    break
        return result


dataset_manager = DatasetManager()
