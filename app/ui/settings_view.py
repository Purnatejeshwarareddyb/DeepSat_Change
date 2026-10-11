from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from app.ui.widgets import SectionPanel
from app.utils.config import config
from app.utils import theme
from app.utils.validators import (
    validate_image_size, validate_batch_size, validate_epochs,
    validate_learning_rate, validate_threshold, validate_min_region_size,
)


class SettingsView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("SETTINGS")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        panel = SectionPanel("MODEL & TRAINING DEFAULTS", theme.ACCENT_PURPLE)

        def add_row(label, widget):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(widget)
            panel.body().addLayout(row)
            return widget

        self.image_size = add_row("IMAGE SIZE", QSpinBox())
        self.image_size.setRange(64, 512)
        self.image_size.setSingleStep(16)
        self.image_size.setValue(config.get("image_size", 256))

        self.batch_size = add_row("BATCH SIZE", QSpinBox())
        self.batch_size.setRange(1, 32)
        self.batch_size.setValue(config.get("batch_size", 4))

        self.epochs = add_row("EPOCHS", QSpinBox())
        self.epochs.setRange(1, 1000)
        self.epochs.setValue(config.get("epochs", 20))

        self.lr = add_row("LEARNING RATE", QDoubleSpinBox())
        self.lr.setDecimals(5)
        self.lr.setRange(0.00001, 1.0)
        self.lr.setValue(config.get("learning_rate", 0.001))

        self.threshold = add_row("CHANGE THRESHOLD", QDoubleSpinBox())
        self.threshold.setRange(0.1, 0.9)
        self.threshold.setSingleStep(0.05)
        self.threshold.setValue(config.get("change_threshold", 0.5))

        self.min_region = add_row("MINIMUM REGION SIZE", QSpinBox())
        self.min_region.setRange(1, 100000)
        self.min_region.setValue(config.get("min_region_size", 100))

        layout.addWidget(panel)

        paths_panel = SectionPanel("PATHS", theme.ACCENT_CYAN)
        self.model_path = QLineEdit(config.get("model_path", "models/best_model.keras"))
        self.dataset_path = QLineEdit(config.get("dataset_path", "dataset"))
        self.output_path = QLineEdit(config.get("output_path", "results"))
        for label, field in [("MODEL PATH", self.model_path), ("DATASET PATH", self.dataset_path), ("OUTPUT PATH", self.output_path)]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(field)
            browse = QPushButton("BROWSE")
            browse.clicked.connect(lambda _, f=field: self._browse(f))
            row.addWidget(browse)
            paths_panel.body().addLayout(row)
        layout.addWidget(paths_panel)

        self.save_btn = QPushButton("SAVE SETTINGS")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
        layout.addStretch()

    def _browse(self, field):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            field.setText(folder)

    def save_settings(self):
        checks = [
            validate_image_size(self.image_size.value()),
            validate_batch_size(self.batch_size.value()),
            validate_epochs(self.epochs.value()),
            validate_learning_rate(self.lr.value()),
            validate_threshold(self.threshold.value()),
            validate_min_region_size(self.min_region.value()),
        ]
        for ok, message in checks:
            if not ok:
                QMessageBox.warning(self, "INVALID SETTING", message)
                return

        config.set("image_size", self.image_size.value())
        config.set("batch_size", self.batch_size.value())
        config.set("epochs", self.epochs.value())
        config.set("learning_rate", self.lr.value())
        config.set("change_threshold", self.threshold.value())
        config.set("min_region_size", self.min_region.value())
        config.set("model_path", self.model_path.text())
        config.set("dataset_path", self.dataset_path.text())
        config.set("output_path", self.output_path.text())
        QMessageBox.information(self, "SETTINGS", "Settings saved successfully.")
