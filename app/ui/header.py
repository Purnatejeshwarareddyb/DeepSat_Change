from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import QTimer, Qt
import time
from app.utils import theme


class Header(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("HeaderPanel")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)

        title_box = QVBoxLayout()
        self.title_label = QLabel("SATELLITE IMAGE CHANGE DETECTION")
        self.title_label.setObjectName("TitleLabel")
        self.subtitle_label = QLabel("Deep Learning Based Change Detection using U-Net")
        self.subtitle_label.setObjectName("SubtitleLabel")
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.subtitle_label)
        layout.addLayout(title_box)
        layout.addStretch()

        clock_box = QVBoxLayout()
        clock_box.setAlignment(Qt.AlignRight)
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(f"font-size:16px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        self.date_label = QLabel()
        self.date_label.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:11px;")
        self.date_label.setAlignment(Qt.AlignRight)
        clock_box.addWidget(self.clock_label, alignment=Qt.AlignRight)
        clock_box.addWidget(self.date_label, alignment=Qt.AlignRight)
        layout.addLayout(clock_box)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        self._tick()

    def _tick(self):
        now = time.localtime()
        self.clock_label.setText(time.strftime("%I:%M:%S %p", now))
        self.date_label.setText(time.strftime("%B %d, %Y  %A", now))

    def set_titles(self, title, subtitle):
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)
