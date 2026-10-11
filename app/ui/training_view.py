from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QDoubleSpinBox,
    QComboBox, QProgressBar, QMessageBox
)
from app.ui.widgets import SectionPanel
from app.ui.charts import LineChartCanvas
from app.workers.training_worker import TrainingWorker
from app.dataset.dataset_manager import dataset_manager
from app.utils.config import config
from app.utils import theme


class TrainingView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.worker = None
        self.history_cache = {"loss": [], "val_loss": [], "dice_metric": [], "val_dice_metric": []}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("TRAINING")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        controls = SectionPanel("TRAINING CONFIGURATION", theme.ACCENT_PURPLE)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("IMAGE SIZE"))
        self.image_size_box = QSpinBox(); self.image_size_box.setRange(64, 512); self.image_size_box.setSingleStep(32)
        self.image_size_box.setValue(config.get("image_size", 256))
        row1.addWidget(self.image_size_box)

        row1.addWidget(QLabel("BATCH SIZE"))
        self.batch_combo = QComboBox(); self.batch_combo.addItems(["1", "2", "4", "8"])
        self.batch_combo.setCurrentText(str(config.get("batch_size", 4)))
        row1.addWidget(self.batch_combo)

        row1.addWidget(QLabel("EPOCHS"))
        self.epochs_box = QSpinBox(); self.epochs_box.setRange(1, 500)
        self.epochs_box.setValue(config.get("epochs", 20))
        row1.addWidget(self.epochs_box)

        row1.addWidget(QLabel("LEARNING RATE"))
        self.lr_box = QDoubleSpinBox(); self.lr_box.setRange(0.00001, 1.0); self.lr_box.setDecimals(5)
        self.lr_box.setSingleStep(0.0001)
        self.lr_box.setValue(config.get("learning_rate", 0.001))
        row1.addWidget(self.lr_box)
        controls.body().addLayout(row1)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("MODEL"))
        self.model_combo = QComboBox(); self.model_combo.addItems(["LIGHTWEIGHT U-NET"])
        model_row.addWidget(self.model_combo)

        model_row.addWidget(QLabel("EARLY STOPPING PATIENCE"))
        self.patience_box = QSpinBox(); self.patience_box.setRange(2, 50)
        self.patience_box.setValue(config.get("early_stopping_patience", 8))
        self.patience_box.setToolTip(
            "Number of epochs with no validation-loss improvement before training "
            "stops early. Raise this if training stops too soon due to noisy "
            "validation loss on a small validation set."
        )
        model_row.addWidget(self.patience_box)
        controls.body().addLayout(model_row)
        layout.addWidget(controls)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("START TRAINING")
        self.start_btn.setObjectName("PrimaryButton")
        self.stop_btn = QPushButton("STOP TRAINING")
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        layout.addLayout(btn_row)

        progress_panel = SectionPanel("TRAINING MODEL", theme.ACCENT_CYAN)
        self.epoch_label = QLabel("Epoch\n0 / 0")
        self.train_loss_label = QLabel("Training Loss\n--")
        self.val_loss_label = QLabel("Validation Loss\n--")
        self.train_dice_label = QLabel("Training Dice\n--")
        self.val_dice_label = QLabel("Validation Dice\n--")
        info_row = QHBoxLayout()
        for lbl in [self.epoch_label, self.train_loss_label, self.val_loss_label, self.train_dice_label, self.val_dice_label]:
            lbl.setStyleSheet(f"color:{theme.TEXT_PRIMARY};")
            info_row.addWidget(lbl)
        progress_panel.body().addLayout(info_row)
        self.progress_bar = QProgressBar()
        progress_panel.body().addWidget(self.progress_bar)
        layout.addWidget(progress_panel)

        chart_panel = SectionPanel("LIVE TRAINING CURVES", theme.ACCENT_PURPLE)
        self.chart = LineChartCanvas(width=6, height=3)
        chart_panel.body().addWidget(self.chart)
        layout.addWidget(chart_panel, stretch=1)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.start_btn.clicked.connect(self.start_training)
        self.stop_btn.clicked.connect(self.stop_training)

    def start_training(self):
        report = dataset_manager.validation_report()
        if not report.get("overall_valid"):
            QMessageBox.warning(self, "DATASET", "No valid matching before/after/mask pairs found. Use the Dataset Manager first.")
            return

        image_size = self.image_size_box.value()
        batch_size = int(self.batch_combo.currentText())
        epochs = self.epochs_box.value()
        lr = self.lr_box.value()
        patience = self.patience_box.value()

        config.set("early_stopping_patience", patience)
        config.set("image_size", image_size)
        config.set("batch_size", batch_size)
        config.set("epochs", epochs)
        config.set("learning_rate", lr)

        self.history_cache = {"loss": [], "val_loss": [], "dice_metric": [], "val_dice_metric": []}
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(epochs)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.worker = TrainingWorker(image_size, batch_size, epochs, lr)
        self.worker.epoch_update.connect(self.on_epoch_update)
        self.worker.finished_ok.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()
        self.status_label.setText("Training started...")

    def stop_training(self):
        if self.worker:
            self.worker.stop()
        self.status_label.setText("Stopping after current epoch...")

    def on_epoch_update(self, epoch, total, logs):
        self.progress_bar.setValue(epoch)
        self.epoch_label.setText(f"Epoch\n{epoch} / {total}")
        self.train_loss_label.setText(f"Training Loss\n{logs.get('loss', 0):.4f}")
        self.val_loss_label.setText(f"Validation Loss\n{logs.get('val_loss', 0):.4f}")
        self.train_dice_label.setText(f"Training Dice\n{logs.get('dice_metric', 0):.4f}")
        self.val_dice_label.setText(f"Validation Dice\n{logs.get('val_dice_metric', 0):.4f}")

        for key in self.history_cache:
            if key in logs:
                self.history_cache[key].append(logs[key])
        self.chart.plot_series({
            "Training Loss": self.history_cache["loss"],
            "Validation Loss": self.history_cache["val_loss"],
        }, xlabel="Epoch", ylabel="Loss")

    def on_finished(self, history, fit_status):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"Training complete. Fit analysis: {fit_status}")
        QMessageBox.information(self, "TRAINING COMPLETE", f"Training finished.\n\nFit analysis: {fit_status}")

    def on_failed(self, message):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "TRAINING FAILED", message)
        self.status_label.setText("Training failed.")
