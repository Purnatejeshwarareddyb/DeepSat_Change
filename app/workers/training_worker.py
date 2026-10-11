from PySide6.QtCore import QThread, Signal
from app.training.trainer import trainer


class TrainingWorker(QThread):
    epoch_update = Signal(int, int, dict)
    finished_ok = Signal(dict, str)
    failed = Signal(str)

    def __init__(self, image_size, batch_size, epochs, learning_rate):
        super().__init__()
        self.image_size = image_size
        self.batch_size = batch_size
        self.epochs = epochs
        self.learning_rate = learning_rate

    def run(self):
        try:
            def on_epoch_end(epoch, total, logs):
                self.epoch_update.emit(epoch, total, logs)

            history, fit_status = trainer.train(
                self.image_size, self.batch_size, self.epochs, self.learning_rate,
                on_epoch_end=on_epoch_end,
            )
            self.finished_ok.emit(history, fit_status)
        except Exception as exc:
            self.failed.emit(str(exc))

    def stop(self):
        trainer.request_stop()
