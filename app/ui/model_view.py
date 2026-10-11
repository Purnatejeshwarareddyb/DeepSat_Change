from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from app.ui.widgets import SectionPanel
from app.models.model_manager import model_manager
from app.utils import theme

FRIENDLY_LABELS = {
    "model_name": "Model Name",
    "input_shape": "Input Shape",
    "total_parameters": "Total Parameters",
    "trainable_parameters": "Trainable Parameters",
    "image_size": "Image Size",
    "epochs": "Epochs Trained",
    "batch_size": "Batch Size",
    "learning_rate": "Learning Rate",
    "optimizer": "Optimizer",
    "loss": "Loss Function",
    "training_date": "Training Date",
    "dataset": "Dataset Path",
}


class ModelView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("MODEL INFORMATION")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        self.status_panel = SectionPanel("MODEL STATUS", theme.ACCENT_CYAN)
        self.status_label = QLabel("Checking...")
        self.status_label.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:14px; font-weight:700;")
        self.status_panel.body().addWidget(self.status_label)
        layout.addWidget(self.status_panel)

        self.details_panel = SectionPanel("MODEL DETAILS", theme.ACCENT_PURPLE)
        self.details_grid = QGridLayout()
        self.details_grid.setHorizontalSpacing(24)
        self.details_grid.setVerticalSpacing(6)
        self.details_panel.body().addLayout(self.details_grid)
        layout.addWidget(self.details_panel)

        metrics_panel = SectionPanel("TRAINING / VALIDATION METRICS", theme.ACCENT_CYAN)
        self.metrics_grid = QGridLayout()
        self.metrics_grid.setHorizontalSpacing(24)
        self.metrics_grid.setVerticalSpacing(6)
        metrics_panel.body().addLayout(self.metrics_grid)
        layout.addWidget(metrics_panel)

        layout.addStretch()

        self.load_btn = QPushButton("LOAD MODEL")
        self.load_btn.setObjectName("PrimaryButton")
        self.load_btn.clicked.connect(self.load_model)
        layout.addWidget(self.load_btn)

        self.refresh()

    def load_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Model File", "", "Keras Model (*.keras)")
        if not path:
            return
        try:
            model_manager.load(path)
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "ERROR", f"Failed to load model: {exc}")

    def _clear_grid(self, grid):
        while grid.count():
            item = grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    def _add_row(self, grid, row, label, value):
        key_label = QLabel(str(label))
        key_label.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:12px;")
        val_label = QLabel(str(value))
        val_label.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:12px; font-weight:700;")
        val_label.setWordWrap(True)
        grid.addWidget(key_label, row, 0, Qt.AlignTop)
        grid.addWidget(val_label, row, 1, Qt.AlignTop)

    def refresh(self):
        self._clear_grid(self.details_grid)
        self._clear_grid(self.metrics_grid)

        if model_manager.model is None:
            model_manager.load()

        if model_manager.model is None:
            self.status_label.setText("NOT TRAINED — train a model on the Training page, or click LOAD MODEL.")
            self.status_label.setStyleSheet(f"color:{theme.WARNING}; font-size:14px; font-weight:700;")
            return

        self.status_label.setText("READY")
        self.status_label.setStyleSheet(f"color:{theme.SUCCESS}; font-size:14px; font-weight:700;")

        info = model_manager.summary_info() or {}
        training_metrics = info.pop("training_metrics", {}) or {}
        validation_metrics = info.pop("validation_metrics", {}) or {}

        row = 0
        for key, value in info.items():
            label = FRIENDLY_LABELS.get(key, key.replace("_", " ").title())
            self._add_row(self.details_grid, row, label, value)
            row += 1

        row = 0
        for key, value in training_metrics.items():
            display = f"{value:.4f}" if isinstance(value, float) else value
            self._add_row(self.metrics_grid, row, f"Train {key.replace('_', ' ').title()}", display)
            row += 1
        for key, value in validation_metrics.items():
            display = f"{value:.4f}" if isinstance(value, float) else value
            self._add_row(self.metrics_grid, row, f"Val {key.replace('_', ' ').title()}", display)
            row += 1

        if row == 0:
            self._add_row(self.metrics_grid, 0, "No metrics recorded", "Train the model to populate this section")
