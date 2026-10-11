import os
import tensorflow as tf


class ProgressCallback(tf.keras.callbacks.Callback):
    def __init__(self, total_epochs, on_epoch_end=None, stop_flag=None):
        super().__init__()
        self.total_epochs = total_epochs
        self.on_epoch_end_cb = on_epoch_end
        self.stop_flag = stop_flag

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        if self.on_epoch_end_cb:
            self.on_epoch_end_cb(epoch + 1, self.total_epochs, logs)
        if self.stop_flag is not None and self.stop_flag.is_set():
            self.model.stop_training = True


def build_callbacks(best_model_path, latest_model_path, log_dir, total_epochs,
                     on_epoch_end=None, stop_flag=None, patience=5):
    os.makedirs(os.path.dirname(best_model_path), exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    checkpoint_best = tf.keras.callbacks.ModelCheckpoint(
        best_model_path, monitor="val_loss", save_best_only=True, verbose=0
    )
    checkpoint_latest = tf.keras.callbacks.ModelCheckpoint(
        latest_model_path, save_best_only=False, verbose=0
    )
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=patience, restore_best_weights=True
    )
    tensorboard = tf.keras.callbacks.TensorBoard(log_dir=log_dir)
    progress = ProgressCallback(total_epochs, on_epoch_end, stop_flag)

    return [checkpoint_best, checkpoint_latest, early_stop, tensorboard, progress]
