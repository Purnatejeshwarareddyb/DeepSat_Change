from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)
from app.ui.widgets import ImagePanel, SectionPanel
from app.preprocessing.image_validator import validate_image, validate_pair
from app.preprocessing.image_loader import load_image_rgb, get_metadata
from app.utils import theme
from app.utils.logger import log


class UploadView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("UPLOAD DATA")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        images_row = QHBoxLayout()
        self.before_panel = ImagePanel("BEFORE IMAGE", theme.SUCCESS)
        self.after_panel = ImagePanel("AFTER IMAGE", theme.ACCENT_CYAN)
        images_row.addWidget(self.before_panel)
        images_row.addWidget(self.after_panel)
        layout.addLayout(images_row, stretch=3)

        meta_row = QHBoxLayout()
        self.meta_before = SectionPanel("BEFORE IMAGE METADATA", theme.SUCCESS)
        self.meta_before_label = QLabel("No image loaded.")
        self.meta_before.body().addWidget(self.meta_before_label)
        self.meta_after = SectionPanel("AFTER IMAGE METADATA", theme.ACCENT_CYAN)
        self.meta_after_label = QLabel("No image loaded.")
        self.meta_after.body().addWidget(self.meta_after_label)
        meta_row.addWidget(self.meta_before)
        meta_row.addWidget(self.meta_after)
        layout.addLayout(meta_row, stretch=2)

        btn_row = QHBoxLayout()
        self.load_before_btn = QPushButton("LOAD BEFORE IMAGE")
        self.load_after_btn = QPushButton("LOAD AFTER IMAGE")
        self.clear_btn = QPushButton("CLEAR")
        self.continue_btn = QPushButton("CONTINUE")
        self.continue_btn.setObjectName("PrimaryButton")
        for b in [self.load_before_btn, self.load_after_btn, self.clear_btn, self.continue_btn]:
            btn_row.addWidget(b)
        layout.addLayout(btn_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color:{theme.TEXT_SECONDARY};")
        layout.addWidget(self.status_label)

        self.load_before_btn.clicked.connect(self.load_before)
        self.load_after_btn.clicked.connect(self.load_after)
        self.clear_btn.clicked.connect(self.clear_all)
        self.continue_btn.clicked.connect(self.check_pair)

    def _format_metadata(self, meta):
        return (f"Filename : {meta['filename']}\n"
                f"Width : {meta['width']}\nHeight : {meta['height']}\n"
                f"Channels : {meta['channels']}\nFile Size : {meta['file_size']} bytes\n"
                f"Format : {meta['format']}")

    def load_before(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Before Image", "", "Images (*.png *.jpg *.jpeg *.tif *.tiff)")
        if not path:
            return
        result = validate_image(path)
        if not result.is_valid:
            QMessageBox.warning(self, "ERROR", result.message)
            return
        self.app_state.before_path = path
        self.before_panel.set_image(load_image_rgb(path))
        self.meta_before_label.setText(self._format_metadata(get_metadata(path)))
        self.status_label.setText("Before image loaded successfully.")
        log.info("Images uploaded successfully")

    def load_after(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select After Image", "", "Images (*.png *.jpg *.jpeg *.tif *.tiff)")
        if not path:
            return
        result = validate_image(path)
        if not result.is_valid:
            QMessageBox.warning(self, "ERROR", result.message)
            return
        self.app_state.after_path = path
        self.after_panel.set_image(load_image_rgb(path))
        self.meta_after_label.setText(self._format_metadata(get_metadata(path)))
        self.status_label.setText("After image loaded successfully.")

    def clear_all(self):
        self.app_state.before_path = None
        self.app_state.after_path = None
        self.before_panel.set_image(None)
        self.after_panel.set_image(None)
        self.meta_before_label.setText("No image loaded.")
        self.meta_after_label.setText("No image loaded.")
        self.status_label.setText("Cleared.")

    def check_pair(self):
        if not self.app_state.before_path or not self.app_state.after_path:
            QMessageBox.warning(self, "ERROR", "Please load both the before and after images.")
            return
        result = validate_pair(self.app_state.before_path, self.app_state.after_path)
        if not result.is_valid and result.metadata.get("mismatch"):
            reply = QMessageBox.question(self, "ERROR",
                                          "The selected images have different dimensions.\n\nWould you like to resize them automatically?")
            if reply == QMessageBox.Yes:
                self.status_label.setText("Images will be resized automatically during preprocessing.")
            return
        elif not result.is_valid:
            QMessageBox.warning(self, "ERROR", result.message)
            return
        self.status_label.setText("Both images validated. Proceed to Preprocessing or Prediction.")
