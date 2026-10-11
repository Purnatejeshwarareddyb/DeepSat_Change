from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QMessageBox
)
from PySide6.QtCore import Qt
from app.ui.widgets import SectionPanel
from app.preprocessing.image_loader import load_image_bgr
from app.workers.inference_worker import InferenceWorker
from app.models.model_manager import model_manager
from app.utils import theme
from app.utils.config import config


class PredictionView(QWidget):
    def __init__(self, app_state, on_result=None):
        super().__init__()
        self.app_state = app_state
        self.on_result = on_result
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("PREDICTION")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        controls = SectionPanel("DETECTION SETTINGS", theme.ACCENT_PURPLE)
        thresh_row = QHBoxLayout()
        thresh_row.addWidget(QLabel("DETECTION THRESHOLD"))
        self.thresh_slider = QSlider(Qt.Horizontal)
        self.thresh_slider.setRange(10, 90)
        self.thresh_slider.setValue(int(config.get("change_threshold", 0.5) * 100))
        self.thresh_value = QLabel(f"{self.thresh_slider.value()/100:.2f}")
        self.thresh_slider.valueChanged.connect(lambda v: self.thresh_value.setText(f"{v/100:.2f}"))
        thresh_row.addWidget(self.thresh_slider)
        thresh_row.addWidget(self.thresh_value)
        controls.body().addLayout(thresh_row)
        layout.addWidget(controls)

        self.stage_label = QLabel("STAGE: IDLE")
        self.stage_label.setStyleSheet(f"color:{theme.ACCENT_CYAN}; font-weight:700;")
        layout.addWidget(self.stage_label)

        self.run_btn = QPushButton("RUN ANALYSIS")
        self.run_btn.setObjectName("PrimaryButton")
        self.run_btn.clicked.connect(self.run_analysis)
        layout.addWidget(self.run_btn)

        layout.addStretch()

    def run_analysis(self):
        if not self.app_state.before_path or not self.app_state.after_path:
            QMessageBox.warning(self, "ERROR", "Please upload both images first (Upload Data page).")
            return
        if model_manager.model is None:
            model_manager.load()
        if model_manager.model is None:
            QMessageBox.warning(self, "MODEL STATUS", "No trained model was found. Train a model or load one from Model Information.")
            return

        before = load_image_bgr(self.app_state.before_path)
        after = load_image_bgr(self.app_state.after_path)
        threshold = self.thresh_slider.value() / 100.0

        self.run_btn.setEnabled(False)
        self.worker = InferenceWorker(
            model_manager.model, before, after,
            image_size=config.get("image_size", 256),
            threshold=threshold,
            min_region_size=config.get("min_region_size", 100),
        )
        self.worker.stage_update.connect(lambda s: self.stage_label.setText(f"STAGE: {s}"))
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _on_finished(self, result):
        self.run_btn.setEnabled(True)
        self.app_state.last_result = result
        if self.on_result:
            self.on_result(result)

    def _on_failed(self, message):
        self.run_btn.setEnabled(True)
        QMessageBox.critical(self, "ERROR", f"Prediction failed: {message}")
        self.stage_label.setText("STAGE: FAILED")
