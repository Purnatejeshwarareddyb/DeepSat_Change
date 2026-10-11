from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from app.ui.widgets import SectionPanel
from app.utils import theme

ABOUT_TEXT = """DEEPSAT-CHANGE

Deep Learning-Based Satellite Image
Change Detection and Analysis System

Course:
INT422 - Deep Learning

Technology:
Python
TensorFlow
Keras
PySide6
OpenCV

Model:
Lightweight U-Net

Purpose:
Detect and analyze geographical changes
between multi-temporal satellite images."""


class AboutView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        panel = SectionPanel("ABOUT PROJECT", theme.ACCENT_PURPLE)
        label = QLabel(ABOUT_TEXT)
        label.setStyleSheet(f"color:{theme.TEXT_PRIMARY}; font-size:13px;")
        panel.body().addWidget(label)
        layout.addWidget(panel)
        layout.addStretch()
