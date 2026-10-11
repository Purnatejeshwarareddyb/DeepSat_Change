from PySide6.QtCore import QThread, Signal
from app.detection.inference import run_inference


class InferenceWorker(QThread):
    stage_update = Signal(str)
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, model, before_bgr, after_bgr, image_size, threshold, min_region_size, do_alignment=True):
        super().__init__()
        self.model = model
        self.before_bgr = before_bgr
        self.after_bgr = after_bgr
        self.image_size = image_size
        self.threshold = threshold
        self.min_region_size = min_region_size
        self.do_alignment = do_alignment

    def run(self):
        try:
            self.stage_update.emit("LOADING")
            self.stage_update.emit("ALIGNMENT")
            self.stage_update.emit("PREPROCESSING")
            self.stage_update.emit("MODEL INFERENCE")
            result = run_inference(
                self.model, self.before_bgr, self.after_bgr,
                image_size=self.image_size, threshold=self.threshold,
                min_region_size=self.min_region_size, do_alignment=self.do_alignment,
            )
            self.stage_update.emit("POST-PROCESSING")
            self.stage_update.emit("REGION ANALYSIS")
            self.stage_update.emit("METRIC CALCULATION")
            self.stage_update.emit("COMPLETE")
            self.finished_ok.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))
