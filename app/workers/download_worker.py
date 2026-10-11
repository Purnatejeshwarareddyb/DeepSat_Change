from PySide6.QtCore import QThread, Signal
from app.dataset.dataset_downloader import download_dataset


class DownloadWorker(QThread):
    progress = Signal(float, int, int)
    finished_ok = Signal(str)
    failed = Signal(str)

    def __init__(self, dataset_entry):
        super().__init__()
        self.dataset_entry = dataset_entry

    def run(self):
        try:
            def cb(percent, downloaded, total):
                self.progress.emit(percent, downloaded, total)
            dest = download_dataset(self.dataset_entry, progress_callback=cb)
            self.finished_ok.emit(dest)
        except Exception as exc:
            self.failed.emit(str(exc))
