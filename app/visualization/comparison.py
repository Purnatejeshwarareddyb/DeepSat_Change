import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QImage, QPixmap, QPainter
from PySide6.QtCore import Qt, QRect
from app.utils import theme


def numpy_to_qimage(array):
    arr = np.ascontiguousarray(array)
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    if arr.ndim == 2:
        h, w = arr.shape
        return QImage(arr.data, w, h, w, QImage.Format_Grayscale8).copy()
    h, w, c = arr.shape
    return QImage(arr.data, w, h, w * c, QImage.Format_RGB888).copy()


class ComparisonSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.before_image = None
        self.after_image = None
        self.divider_ratio = 0.5
        self.dragging = False
        self.setMinimumHeight(320)
        self.setMouseTracking(True)
        self.setStyleSheet(f"background-color:{theme.BG_PANEL_LIGHT}; border-radius:6px;")

    def set_images(self, before_array, after_array):
        self.before_image = numpy_to_qimage(before_array) if before_array is not None else None
        self.after_image = numpy_to_qimage(after_array) if after_array is not None else None
        self.update()

    def _scaled_rect(self, image):
        if image is None:
            return QRect()
        target = self.rect()
        img_ratio = image.width() / image.height()
        target_ratio = target.width() / target.height()
        if img_ratio > target_ratio:
            w = target.width()
            h = int(w / img_ratio)
        else:
            h = target.height()
            w = int(h * img_ratio)
        x = (target.width() - w) // 2
        y = (target.height() - h) // 2
        return QRect(x, y, w, h)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        if self.after_image is None or self.before_image is None:
            painter.setPen(theme.TEXT_SECONDARY)
            painter.drawText(self.rect(), Qt.AlignCenter, "LOAD BOTH IMAGES TO COMPARE")
            return

        rect = self._scaled_rect(self.after_image)
        painter.drawImage(rect, self.after_image)

        divider_x = int(rect.x() + rect.width() * self.divider_ratio)
        before_rect = QRect(rect.x(), rect.y(), max(0, divider_x - rect.x()), rect.height())
        painter.setClipRect(before_rect)
        painter.drawImage(rect, self.before_image)
        painter.setClipping(False)

        painter.setPen(theme.ACCENT_CYAN)
        painter.drawLine(divider_x, rect.y(), divider_x, rect.y() + rect.height())
        painter.setBrush(Qt.white)
        painter.drawEllipse(divider_x - 6, rect.y() + rect.height() // 2 - 6, 12, 12)

        painter.setPen(theme.TEXT_PRIMARY)
        painter.drawText(rect.x() + 8, rect.y() + 18, "BEFORE")
        painter.drawText(rect.x() + rect.width() - 50, rect.y() + 18, "AFTER")

    def mousePressEvent(self, event):
        self.dragging = True
        self._update_divider(event.position().x())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self._update_divider(event.position().x())

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def _update_divider(self, x):
        rect = self._scaled_rect(self.after_image) if self.after_image else self.rect()
        if rect.width() == 0:
            return
        ratio = (x - rect.x()) / rect.width()
        self.divider_ratio = min(1.0, max(0.0, ratio))
        self.update()
