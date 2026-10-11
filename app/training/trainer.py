import os
import time
import threading
from app.models.model_manager import model_manager
from app.training.dataset_loader import build_dataset
from app.training.callbacks import build_callbacks
from app.dataset.dataset_manager import dataset_manager
from app.training.data_validation import validate_for_training, DatasetTrainingError
from app.training.training_history import save_run
from app.utils.config import config, ROOT_DIR
from app.utils.helpers import timestamp, fit_analysis
from app.utils.logger import log
from app.database.database import db


class Trainer:
    def __init__(self):
        self.stop_flag = threading.Event()

    def request_stop(self):
        self.stop_flag.set()

    def train(self, image_size, batch_size, epochs, learning_rate, on_epoch_end=None):
        self.stop_flag.clear()
        try:
            validation_summary = validate_for_training(dataset_manager)
        except DatasetTrainingError as exc:
            raise RuntimeError(str(exc))
        if validation_summary["warning"]:
            log.warning(validation_summary["warning"])

        train_ids = dataset_manager.matching_pairs("train")
        val_ids = dataset_manager.matching_pairs("validation") or dataset_manager.matching_pairs("test")

        if not val_ids:
            val_ids = train_ids[: max(1, len(train_ids) // 5)]

        train_ds = build_dataset(train_ids, dataset_manager, "train", image_size, batch_size, augment=True)
        val_split = "validation" if dataset_manager.matching_pairs("validation") else "test"
        val_ds = build_dataset(val_ids, dataset_manager, val_split, image_size, batch_size, augment=False, shuffle=False)

        model_manager.build_new(image_size=image_size)
        model_manager.model.optimizer.learning_rate.assign(learning_rate)

        log_dir = os.path.join(ROOT_DIR, "logs", "tensorboard", time.strftime("%Y%m%d-%H%M%S"))
        callbacks = build_callbacks(
            model_manager.best_model_path(),
            model_manager.latest_model_path(),
            log_dir,
            epochs,
            on_epoch_end=on_epoch_end,
            stop_flag=self.stop_flag,
            patience=config.get("early_stopping_patience", 8),
        )

        started_at = timestamp()
        history = model_manager.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs,
            callbacks=callbacks,
            verbose=0,
        )
        finished_at = timestamp()

        hist = history.history
        fit_status = fit_analysis(hist.get("loss", []), hist.get("val_loss", []))

        metadata = {
            "model_name": "Lightweight U-Net",
            "input_shape": f"{image_size}x{image_size}x6",
            "image_size": image_size,
            "epochs": len(hist.get("loss", [])),
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "optimizer": "Adam",
            "loss": "Binary Crossentropy + Dice Loss",
            "training_date": finished_at,
            "dataset": config.get("dataset_path"),
            "training_metrics": {k: v[-1] for k, v in hist.items() if not k.startswith("val_")},
            "validation_metrics": {k: v[-1] for k, v in hist.items() if k.startswith("val_")},
        }
        model_manager.save(model_manager.latest_model_path(), metadata)

        db.insert_training_run({
            "started_at": started_at,
            "finished_at": finished_at,
            "epochs": len(hist.get("loss", [])),
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "final_train_loss": hist.get("loss", [0])[-1],
            "final_val_loss": hist.get("val_loss", [0])[-1],
            "final_val_dice": hist.get("val_dice_metric", [0])[-1] if "val_dice_metric" in hist else 0,
            "final_val_iou": hist.get("val_iou_metric", [0])[-1] if "val_iou_metric" in hist else 0,
            "fit_status": fit_status,
            "history": hist,
        })

        save_run(hist, fit_status, {
            "image_size": image_size,
            "batch_size": batch_size,
            "epochs": epochs,
            "learning_rate": learning_rate,
            "started_at": started_at,
            "finished_at": finished_at,
        })

        log.info("Model saved successfully after training")
        return hist, fit_status


trainer = Trainer()
