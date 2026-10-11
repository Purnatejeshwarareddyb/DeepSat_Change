from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from app.ui.widgets import SectionPanel, StatCard
from app.visualization.image_viewer import ZoomableImagePanel
from app.utils import theme


class ResultsView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("RESULTS")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        images_row = QHBoxLayout()
        self.before_panel = ZoomableImagePanel("BEFORE IMAGE", theme.SUCCESS)
        self.after_panel = ZoomableImagePanel("AFTER IMAGE", theme.ACCENT_CYAN)
        self.mask_panel = ZoomableImagePanel("PREDICTED CHANGE MASK", theme.ACCENT_PURPLE)
        self.overlay_panel = ZoomableImagePanel("OVERLAY", theme.ACCENT_PINK)
        for p in [self.before_panel, self.after_panel, self.mask_panel, self.overlay_panel]:
            images_row.addWidget(p)
        layout.addLayout(images_row, stretch=3)

        stats_row = QHBoxLayout()
        self.change_card = StatCard("CHANGE PERCENTAGE", "--", theme.ACCENT_CYAN)
        self.severity_card = StatCard("SEVERITY", "--", theme.WARNING)
        self.regions_card = StatCard("REGIONS DETECTED", "--", theme.ACCENT_PURPLE)
        self.confidence_card = StatCard("CONFIDENCE", "--", theme.SUCCESS)
        self.time_card = StatCard("PROCESSING TIME", "--", theme.ACCENT_PINK)
        for c in [self.change_card, self.severity_card, self.regions_card, self.confidence_card, self.time_card]:
            stats_row.addWidget(c)
        layout.addLayout(stats_row)

        region_panel = SectionPanel("DETECTED REGIONS", theme.ACCENT_CYAN)
        self.region_table = QTableWidget(0, 6)
        self.region_table.setHorizontalHeaderLabels(["Region ID", "Area", "Width", "Height", "Centroid", "Relative Area %"])
        self.region_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        region_panel.body().addWidget(self.region_table)
        layout.addWidget(region_panel, stretch=2)

    def display_result(self, result):
        self.before_panel.set_image(result.before_display)
        self.after_panel.set_image(result.after_display)
        self.mask_panel.set_image((result.binary_mask * 255).astype("uint8"))
        self.overlay_panel.set_image(result.overlay)

        stats = result.change_stats
        self.change_card.set_value(f"{stats.get('change_percent', 0):.2f}%")
        self.severity_card.set_value(stats.get("severity", "--"))
        self.regions_card.set_value(len(result.regions))
        self.confidence_card.set_value(f"{stats.get('confidence', 0):.4f}")
        self.time_card.set_value(f"{result.timings.get('total_time', 0):.2f}s")

        self.region_table.setRowCount(len(result.regions))
        for row, r in enumerate(result.regions):
            values = [r["region_id"], r["area"], r["width"], r["height"],
                      f"{r['centroid'][0]}, {r['centroid'][1]}", f"{r['relative_area']}%"]
            for col, val in enumerate(values):
                self.region_table.setItem(row, col, QTableWidgetItem(str(val)))
