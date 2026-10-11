import threading
from PySide6.QtCore import QThread, Signal
from app.dataset.hf_downloader import download_via_huggingface


class HFDatasetWorker(QThread):
    progress = Signal(str, int)
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, dataset_entry):
        super().__init__()
        self.dataset_entry = dataset_entry
        self.stop_flag = threading.Event()

    def run(self):
        try:
            def cb(split, count):
                self.progress.emit(split, count)
            counts = download_via_huggingface(self.dataset_entry, progress_callback=cb, stop_flag=self.stop_flag)
            self.finished_ok.emit(counts)
        except Exception as exc:
            self.failed.emit(str(exc))

    def stop(self):
        self.stop_flag.set()
