from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox
from app.ui.widgets import SectionPanel, ImagePanel
from app.preprocessing.image_loader import load_image_bgr
from app.preprocessing.image_registration import align_images
from app.preprocessing.preprocessing import preprocess_pair, resize_to_match
from app.utils import theme
from app.utils.config import config

STEPS = ["Image Loading", "Image Validation", "Image Alignment", "Resizing",
         "Normalization", "Tensor Conversion", "Model Input Preparation"]


class PreprocessingView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("PREPROCESSING PIPELINE")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        self.step_labels = []
        panel = SectionPanel("PIPELINE STEPS", theme.ACCENT_CYAN)
        for i, step in enumerate(STEPS, start=1):
            lbl = QLabel(f"{i}. {step}   —   WAITING")
            lbl.setStyleSheet(f"color:{theme.TEXT_SECONDARY};")
            panel.body().addWidget(lbl)
            self.step_labels.append(lbl)
        layout.addWidget(panel)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        images_row = QVBoxLayout()
        self.aligned_panel = ImagePanel("ALIGNED AFTER IMAGE PREVIEW", theme.ACCENT_PURPLE)
        images_row.addWidget(self.aligned_panel)
        layout.addLayout(images_row, stretch=2)

        self.status_label = QLabel("Status: idle")
        layout.addWidget(self.status_label)

        self.run_btn = QPushButton("RUN PREPROCESSING")
        self.run_btn.setObjectName("PrimaryButton")
        self.run_btn.clicked.connect(self.run_pipeline)
        layout.addWidget(self.run_btn)

    def _mark(self, index, state):
        colors = {"waiting": theme.TEXT_SECONDARY, "running": theme.WARNING, "done": theme.SUCCESS, "failed": theme.ERROR}
        text = STEPS[index]
        self.step_labels[index].setText(f"{index + 1}. {text}   —   {state.upper()}")
        self.step_labels[index].setStyleSheet(f"color:{colors[state]};")

    def run_pipeline(self):
        if not self.app_state.before_path or not self.app_state.after_path:
            QMessageBox.warning(self, "ERROR", "Please upload both images first (Upload Data page).")
            return

        for i in range(len(STEPS)):
            self._mark(i, "waiting")
        self.progress.setValue(0)

        try:
            self._mark(0, "running")
            before = load_image_bgr(self.app_state.before_path)
            after = load_image_bgr(self.app_state.after_path)
            self._mark(0, "done"); self.progress.setValue(15)

            self._mark(1, "done"); self.progress.setValue(28)

            self._mark(2, "running")
            if before.shape[:2] != after.shape[:2]:
                before, after = resize_to_match(before, after)
            aligned, ok, msg = align_images(before, after)
            self._mark(2, "done" if ok else "failed")
            self.status_label.setText(f"ALIGNMENT STATUS: {'SUCCESS' if ok else 'FAILED'} — {msg}")
            self.progress.setValue(50)
            after_used = aligned if ok else after

            self._mark(3, "running")
            image_size = config.get("image_size", 256)
            self._mark(3, "done"); self.progress.setValue(65)

            self._mark(4, "running")
            tensor, before_r, after_r = preprocess_pair(before, after_used, image_size)
            self._mark(4, "done"); self.progress.setValue(80)

            self._mark(5, "done"); self.progress.setValue(90)
            self._mark(6, "done"); self.progress.setValue(100)

            self.aligned_panel.set_image(after_r)
            self.app_state.preprocessed_tensor = tensor
            self.app_state.before_display = before_r
            self.app_state.after_display = after_r
            self.status_label.setText("Preprocessing completed successfully.")
        except Exception as exc:
            QMessageBox.critical(self, "ERROR", f"Preprocessing failed: {exc}")
