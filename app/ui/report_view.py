import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from app.ui.widgets import SectionPanel
from app.utils import theme
from app.utils.config import ROOT_DIR
from app.utils.helpers import ensure_dir, timestamp
from app.reports.pdf_report import generate_report
from app.reports.csv_export import export_regions_csv
from app.reports.json_export import export_analysis_json
from app.models.model_manager import model_manager
from app.database.database import db
import cv2
import numpy as np


class ReportView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("REPORT GENERATOR")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        panel = SectionPanel("EXPORT OPTIONS", theme.ACCENT_PURPLE)
        row1 = QHBoxLayout()
        self.export_mask_btn = QPushButton("EXPORT CHANGE MASK")
        self.export_overlay_btn = QPushButton("EXPORT OVERLAY")
        self.export_heatmap_btn = QPushButton("EXPORT HEATMAP")
        row1.addWidget(self.export_mask_btn)
        row1.addWidget(self.export_overlay_btn)
        row1.addWidget(self.export_heatmap_btn)
        panel.body().addLayout(row1)

        row2 = QHBoxLayout()
        self.export_csv_btn = QPushButton("EXPORT CSV")
        self.export_json_btn = QPushButton("EXPORT JSON")
        self.export_pdf_btn = QPushButton("EXPORT PDF REPORT")
        self.export_pdf_btn.setObjectName("SuccessButton")
        row2.addWidget(self.export_csv_btn)
        row2.addWidget(self.export_json_btn)
        row2.addWidget(self.export_pdf_btn)
        panel.body().addLayout(row2)
        layout.addWidget(panel)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.export_mask_btn.clicked.connect(lambda: self._export_image("binary_mask", "masks", scale255=True))
        self.export_overlay_btn.clicked.connect(lambda: self._export_image("overlay", "overlays"))
        self.export_heatmap_btn.clicked.connect(self.export_heatmap)
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_pdf_btn.clicked.connect(self.export_pdf)

    def _result(self):
        result = self.app_state.last_result
        if result is None:
            QMessageBox.warning(self, "ERROR", "Run an analysis first (Prediction page).")
        return result

    def _export_image(self, attr, subfolder, scale255=False):
        result = self._result()
        if result is None:
            return
        arr = getattr(result, attr)
        if scale255:
            arr = (arr * 255).astype(np.uint8)
        out_dir = ensure_dir(os.path.join(ROOT_DIR, "results", subfolder))
        path = os.path.join(out_dir, f"{attr}_{timestamp().replace(':', '-').replace(' ', '_')}.png")
        cv2.imwrite(path, cv2.cvtColor(arr, cv2.COLOR_RGB2BGR) if arr.ndim == 3 else arr)
        self.status_label.setText(f"Saved: {path}")

    def export_heatmap(self):
        result = self._result()
        if result is None:
            return
        from app.visualization.heatmap import probability_to_heatmap
        heat = probability_to_heatmap(result.probability_map)
        out_dir = ensure_dir(os.path.join(ROOT_DIR, "results", "heatmaps"))
        path = os.path.join(out_dir, f"heatmap_{timestamp().replace(':', '-').replace(' ', '_')}.png")
        cv2.imwrite(path, cv2.cvtColor(heat, cv2.COLOR_RGB2BGR))
        self.status_label.setText(f"Saved: {path}")

    def export_csv(self):
        result = self._result()
        if result is None:
            return
        out_dir = ensure_dir(os.path.join(ROOT_DIR, "results", "exports"))
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", os.path.join(out_dir, "regions.csv"), "CSV Files (*.csv)")
        if not path:
            return
        export_regions_csv(result.regions, path)
        self.status_label.setText(f"Saved: {path}")

    def export_json(self):
        result = self._result()
        if result is None:
            return
        out_dir = ensure_dir(os.path.join(ROOT_DIR, "results", "exports"))
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", os.path.join(out_dir, "analysis.json"), "JSON Files (*.json)")
        if not path:
            return
        metadata = {"processing_time": result.timings, "alignment": result.alignment_message}
        export_analysis_json(metadata, result.change_stats, result.regions, path)
        self.status_label.setText(f"Saved: {path}")

    def export_pdf(self):
        result = self._result()
        if result is None:
            return
        out_dir = ensure_dir(os.path.join(ROOT_DIR, "results", "reports"))
        tmp_dir = ensure_dir(os.path.join(ROOT_DIR, "results", "exports", "tmp"))

        def save_tmp(arr, name):
            p = os.path.join(tmp_dir, name)
            if arr.ndim == 2:
                cv2.imwrite(p, arr)
            else:
                cv2.imwrite(p, cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
            return p

        before_p = save_tmp(result.before_display, "before.png")
        after_p = save_tmp(result.after_display, "after.png")
        mask_p = save_tmp((result.binary_mask * 255).astype(np.uint8), "mask.png")
        overlay_p = save_tmp(result.overlay, "overlay.png")

        path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", os.path.join(out_dir, "deepsat_report.pdf"), "PDF Files (*.pdf)")
        if not path:
            return

        model_info = model_manager.summary_info() or {}
        metrics = self.app_state.last_metrics or {}
        try:
            generate_report(path, before_p, after_p, mask_p, overlay_p, result.change_stats, metrics, result.regions, model_info)
            self.status_label.setText(f"Report saved: {path}")

            db.insert_analysis({
                "before_image": self.app_state.before_path or "",
                "after_image": self.app_state.after_path or "",
                "model_name": model_info.get("model_name", "Lightweight U-Net"),
                "change_percent": result.change_stats.get("change_percent", 0.0),
                "num_regions": len(result.regions),
                "confidence": result.change_stats.get("confidence", 0.0),
                "processing_time": result.timings.get("total_time", 0.0),
                "severity": result.change_stats.get("severity", ""),
                "mask_path": mask_p,
                "overlay_path": overlay_p,
                "metrics": metrics,
            })
        except Exception as exc:
            QMessageBox.critical(self, "ERROR", f"PDF generation failed: {exc}")
