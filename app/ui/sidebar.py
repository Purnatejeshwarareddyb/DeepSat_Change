from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Signal, Qt
from app.utils import theme

NAV_ITEMS = [
    ("DASHBOARD", "dashboard"),
    ("UPLOAD DATA", "upload"),
    ("PREPROCESSING", "preprocessing"),
    ("PREDICTION", "prediction"),
    ("RESULTS", "results"),
    ("VISUALIZATION", "visualization"),
    ("ACTIVATION MAPS", "activation"),
    ("METRICS", "metrics"),
    ("TRAINING", "training"),
    ("DATASET MANAGER", "dataset"),
    ("REPORT GENERATOR", "report"),
    ("HISTORY", "history"),
    ("MODEL INFORMATION", "model"),
    ("SETTINGS", "settings"),
    ("ABOUT PROJECT", "about"),
]


class Sidebar(QWidget):
    navigate = Signal(str)
    exit_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(230)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 20, 18, 20)
        name_label = QLabel("DEEPSAT-CHANGE")
        name_label.setStyleSheet(f"font-weight:800; font-size:15px; color:{theme.TEXT_PRIMARY}; letter-spacing:1px;")
        version_label = QLabel("v1.0")
        version_label.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:11px;")
        header_layout.addWidget(name_label)
        header_layout.addWidget(version_label)
        layout.addWidget(header)

        self.buttons = {}
        for label, key in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("NavButton")
            btn.setProperty("active", "false")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self.navigate.emit(k))
            layout.addWidget(btn)
            self.buttons[key] = btn

        layout.addStretch()

        exit_btn = QPushButton("EXIT APPLICATION")
        exit_btn.setObjectName("NavButton")
        exit_btn.setStyleSheet(f"color:{theme.ERROR};")
        exit_btn.clicked.connect(self.exit_requested.emit)
        layout.addWidget(exit_btn)

    def set_active(self, key):
        for k, btn in self.buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()
