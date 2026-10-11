from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QProgressBar
)
from app.ui.widgets import SectionPanel
from app.dataset.dataset_manager import dataset_manager
from app.workers.hf_dataset_worker import HFDatasetWorker
from app.workers.download_worker import DownloadWorker
from app.utils.config import config
from app.utils import theme


class DatasetView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("DATASET MANAGER")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        registry = config.load_datasets_registry().get("available_datasets", [])
        self.dataset_entry = registry[0] if registry else {}

        info_panel = SectionPanel("AVAILABLE DATASET", theme.ACCENT_CYAN)
        self.info_label = QLabel(self._format_info())
        self.info_label.setStyleSheet(f"color:{theme.TEXT_PRIMARY};")
        self.info_label.setWordWrap(True)
        info_panel.body().addWidget(self.info_label)
        note = QLabel("Downloading requires no account, login, or manual steps. "
                       "Files are fetched, organized into train/validation/test, and validated automatically.")
        note.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:11px;")
        note.setWordWrap(True)
        info_panel.body().addWidget(note)
        layout.addWidget(info_panel)

        btn_row = QHBoxLayout()
        self.download_btn = QPushButton("DOWNLOAD DATASET")
        self.download_btn.setObjectName("PrimaryButton")
        self.cancel_btn = QPushButton("CANCEL DOWNLOAD")
        self.cancel_btn.setEnabled(False)
        self.local_btn = QPushButton("USE LOCAL DATASET")
        btn_row.addWidget(self.download_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.local_btn)
        layout.addLayout(btn_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color:{theme.ACCENT_CYAN};")
        layout.addWidget(self.progress_label)

        validation_panel = SectionPanel("DATASET VALIDATION", theme.ACCENT_PURPLE)
        self.validation_label = QLabel("Not validated yet.")
        self.validation_label.setStyleSheet(f"color:{theme.TEXT_PRIMARY};")
        validation_panel.body().addWidget(self.validation_label)
        self.validate_btn = QPushButton("VALIDATE DATASET")
        validation_panel.body().addWidget(self.validate_btn)
        layout.addWidget(validation_panel, stretch=1)

        self.download_btn.clicked.connect(self.download_dataset)
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.local_btn.clicked.connect(self.select_local)
        self.validate_btn.clicked.connect(self.validate)

        self.validate()

    def _format_info(self):
        e = self.dataset_entry
        return (f"Dataset : {e.get('name', 'N/A')}\n"
                f"Type : {e.get('type', '-')}\n"
                f"Approximate Size : {e.get('approx_size', '-')}\n"
                f"License : {e.get('license', '-')}\n"
                f"Homepage : {e.get('homepage_url', '-')}")

    def download_dataset(self):
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_label.setText("Connecting to Hugging Face and starting download...")

        if self.dataset_entry.get("huggingface_dataset_id"):
            self.worker = HFDatasetWorker(self.dataset_entry)
            self.worker.progress.connect(self._on_hf_progress)
            self.worker.finished_ok.connect(self._on_hf_done)
            self.worker.failed.connect(self._on_download_failed)
            self.worker.start()
            return

        if not self.dataset_entry.get("download_url"):
            self.download_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.progress_bar.setVisible(False)
            QMessageBox.information(
                self, "DATASET MANAGER",
                "No automated download is configured for this dataset entry.\n\n"
                "Please download it manually, then use USE LOCAL DATASET."
            )
            return

        self.progress_bar.setRange(0, 100)
        self.worker = DownloadWorker(self.dataset_entry)
        self.worker.progress.connect(lambda pct, d, t: self.progress_bar.setValue(int(pct)))
        self.worker.finished_ok.connect(self._on_download_done)
        self.worker.failed.connect(self._on_download_failed)
        self.worker.start()

    def cancel_download(self):
        if self.worker is not None and hasattr(self.worker, "stop"):
            self.worker.stop()
        self.progress_label.setText("Cancelling...")

    def _on_hf_progress(self, split, count):
        self.progress_label.setText(f"Downloading and organizing images...  {split.upper()}: {count} saved")

    def _on_hf_done(self, counts):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        QMessageBox.information(
            self, "DATASET READY",
            f"Dataset downloaded and organized automatically.\n\n"
            f"Training Images: {counts.get('train', 0)}\n"
            f"Validation Images: {counts.get('validation', 0)}\n"
            f"Test Images: {counts.get('test', 0)}"
        )
        self.progress_label.setText("Download complete.")
        self.validate()

    def _on_download_done(self, dest):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "DATASET READY", f"Dataset downloaded and extracted to:\n{dest}")
        self.validate()

    def _on_download_failed(self, message):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Download failed.")
        QMessageBox.critical(self, "DOWNLOAD FAILED", message)

    def select_local(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if not folder:
            return
        dataset_manager.set_local_dataset(folder)
        self.validate()

    def validate(self):
        report = dataset_manager.validation_report()
        lines = []
        for split in ["train", "validation", "test"]:
            r = report[split]
            lines.append(f"[{split.upper()}]  Before: {r['before_count']}  After: {r['after_count']}  "
                          f"Masks: {r['mask_count']}  Matching: {r['matching_pairs']}  "
                          f"Missing Before: {r['missing_before']}  Missing After: {r['missing_after']}  "
                          f"Missing Masks: {r['missing_mask']}")
        status = "VALID" if report.get("overall_valid") else "NOT VALID (no matching pairs found)"
        lines.append(f"\nSTATUS: {status}")
        self.validation_label.setText("\n".join(lines))
