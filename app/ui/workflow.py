from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QColor
from app.utils import theme

STEPS = [
    ("1", "UPLOAD IMAGES", "Load Before & After", theme.SUCCESS),
    ("2", "PREPROCESSING", "Image Preparation", theme.ACCENT_CYAN),
    ("3", "MODEL PREDICTION", "U-Net Inference", theme.ACCENT_PURPLE),
    ("4", "ANALYSIS", "Compute Metrics", theme.WARNING),
    ("5", "VISUALIZATION", "Results & Reports", theme.ACCENT_PINK),
]


class StepCircle(QLabel):
    def __init__(self, number, color):
        super().__init__(number)
        self.setFixedSize(46, 46)
        self.setAlignment(Qt.AlignCenter)
        self.color = color
        self.set_state("waiting")

    def set_state(self, state):
        if state == "done":
            style = f"border-radius:23px; border:2px solid {self.color}; background-color:{self.color}; color:#020208; font-weight:800; font-size:16px;"
        elif state == "current":
            style = f"border-radius:23px; border:2px solid {self.color}; background-color:{theme.BG_PANEL_LIGHT}; color:{self.color}; font-weight:800; font-size:16px;"
        elif state == "failed":
            style = f"border-radius:23px; border:2px solid {theme.ERROR}; background-color:{theme.BG_PANEL_LIGHT}; color:{theme.ERROR}; font-weight:800; font-size:16px;"
        else:
            style = f"border-radius:23px; border:2px solid {theme.BORDER}; background-color:{theme.BG_PANEL_LIGHT}; color:{theme.TEXT_SECONDARY}; font-weight:800; font-size:16px;"
        self.setStyleSheet(style)


class WorkflowBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Panel")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        self.circles = []
        for i, (num, title, subtitle, color) in enumerate(STEPS):
            step_box = QVBoxLayout()
            row = QHBoxLayout()
            circle = StepCircle(num, color)
            self.circles.append(circle)
            row.addWidget(circle)
            text_box = QVBoxLayout()
            title_label = QLabel(title)
            title_label.setStyleSheet(f"color:{color}; font-weight:700; font-size:11px; letter-spacing:1px;")
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:10px;")
            text_box.addWidget(title_label)
            text_box.addWidget(subtitle_label)
            row.addLayout(text_box)
            layout.addLayout(row)
            if i < len(STEPS) - 1:
                arrow = QLabel("\u2192")
                arrow.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:18px; padding: 0 14px;")
                layout.addWidget(arrow)
        layout.addStretch()
        self.set_step(0)

    def set_step(self, current_index, failed=False):
        for i, circle in enumerate(self.circles):
            if failed and i == current_index:
                circle.set_state("failed")
            elif i < current_index:
                circle.set_state("done")
            elif i == current_index:
                circle.set_state("current")
            else:
                circle.set_state("waiting")

    def complete_all(self):
        for circle in self.circles:
            circle.set_state("done")

    def reset(self):
        self.set_step(0)
