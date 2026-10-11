import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QStackedWidget
from PySide6.QtCore import Qt
from app.visualization.image_viewer import ZoomableImagePanel
from app.visualization.comparison import ComparisonSlider
from app.visualization.overlays import build_overlay
from app.visualization.heatmap import probability_to_heatmap
from app.utils import theme


class VisualizationView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("VISUALIZATION")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        mode_row = QHBoxLayout()
        self.mask_btn = QPushButton("CHANGE MASK")
        self.prob_btn = QPushButton("PROBABILITY MAP")
        self.overlay_btn = QPushButton("OVERLAY")
        self.compare_btn = QPushButton("BEFORE / AFTER COMPARE")
        for b in [self.mask_btn, self.prob_btn, self.overlay_btn, self.compare_btn]:
            mode_row.addWidget(b)
        layout.addLayout(mode_row)

        self.stack = QStackedWidget()
        self.main_panel = ZoomableImagePanel("VISUALIZATION", theme.ACCENT_PURPLE)
        self.comparison_slider = ComparisonSlider()
        self.stack.addWidget(self.main_panel)
        self.stack.addWidget(self.comparison_slider)
        layout.addWidget(self.stack, stretch=3)

        opacity_row = QHBoxLayout()
        opacity_row.addWidget(QLabel("OVERLAY OPACITY"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        opacity_row.addWidget(self.opacity_slider)
        layout.addLayout(opacity_row)

        self.mask_btn.clicked.connect(lambda: self.show_mode("mask"))
        self.prob_btn.clicked.connect(lambda: self.show_mode("prob"))
        self.overlay_btn.clicked.connect(lambda: self.show_mode("overlay"))
        self.compare_btn.clicked.connect(lambda: self.show_mode("compare"))
        self.opacity_slider.valueChanged.connect(lambda v: self.show_mode("overlay") if self.current_mode == "overlay" else None)

        self.current_mode = "overlay"

    def show_mode(self, mode):
        self.current_mode = mode
        result = self.app_state.last_result
        if result is None:
            return

        if mode == "compare":
            self.stack.setCurrentWidget(self.comparison_slider)
            self.comparison_slider.set_images(result.before_display, result.after_display)
            return

        self.stack.setCurrentWidget(self.main_panel)
        if mode == "mask":
            self.main_panel.set_image((result.binary_mask * 255).astype(np.uint8))
        elif mode == "prob":
            self.main_panel.set_image(probability_to_heatmap(result.probability_map))
        else:
            opacity = self.opacity_slider.value() / 100.0
            overlay = build_overlay(result.after_display, result.binary_mask, opacity=opacity)
            self.main_panel.set_image(overlay)

    def refresh(self):
        self.show_mode(self.current_mode)
