import numpy as np
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from app.utils import theme


def numpy_to_pixmap(array):
    if array is None:
        return QPixmap()
    arr = np.ascontiguousarray(array)
    if arr.ndim == 2:
        arr = (arr * 255).astype(np.uint8) if arr.dtype != np.uint8 else arr
        h, w = arr.shape
        qimg = QImage(arr.data, w, h, w, QImage.Format_Grayscale8)
    else:
        if arr.dtype != np.uint8:
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        h, w, c = arr.shape
        qimg = QImage(arr.data, w, h, w * c, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg.copy())


class ImagePanel(QFrame):
    def __init__(self, title, accent=theme.ACCENT_CYAN):
        super().__init__()
        self.setObjectName("Panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color:{accent}; font-weight:700; letter-spacing:1px; font-size:11px;")
        layout.addWidget(title_label)
        self.image_label = QLabel("NO IMAGE")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(180)
        self.image_label.setStyleSheet(f"background-color:{theme.BG_PANEL_LIGHT}; border-radius:6px; color:{theme.TEXT_SECONDARY};")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.image_label)

    def set_image(self, array):
        pixmap = numpy_to_pixmap(array)
        if pixmap.isNull():
            self.image_label.setText("NO IMAGE")
            return
        scaled = pixmap.scaled(self.image_label.width() or 300, self.image_label.height() or 200,
                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self._pixmap = pixmap

    def resizeEvent(self, event):
        if hasattr(self, "_pixmap"):
            scaled = self._pixmap.scaled(self.image_label.width(), self.image_label.height(),
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        super().resizeEvent(event)


class StatCard(QFrame):
    def __init__(self, label, value="--", accent=theme.ACCENT_CYAN):
        super().__init__()
        self.setObjectName("Card")
        self.setMinimumWidth(120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        self.label_widget = QLabel(label)
        self.label_widget.setObjectName("StatLabel")
        self.label_widget.setWordWrap(True)
        self.value_widget = QLabel(value)
        self.value_widget.setWordWrap(True)
        self.value_widget.setStyleSheet(f"font-size:20px; font-weight:800; color:{accent};")
        layout.addWidget(self.label_widget)
        layout.addWidget(self.value_widget)
        from app.utils.animations import CountUpAnimator
        self.animator = CountUpAnimator(self.value_widget)

    def set_value(self, value):
        self.value_widget.setText(str(value))


class SectionPanel(QFrame):
    def __init__(self, title, accent=theme.ACCENT_PURPLE):
        super().__init__()
        self.setObjectName("Panel")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setAlignment(Qt.AlignTop)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color:{accent}; font-weight:700; letter-spacing:1px; font-size:11px;")
        self.layout.addWidget(title_label)

    def body(self):
        return self.layout
