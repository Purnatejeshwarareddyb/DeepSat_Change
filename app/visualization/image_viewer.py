import numpy as np
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtGui import QImage, QPixmap, QPainter
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


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap_item = None
        self._zoom = 0

    def set_array(self, array):
        pixmap = numpy_to_pixmap(array)
        self._scene.clear()
        if pixmap.isNull():
            self._pixmap_item = None
            return
        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self._pixmap_item)
        self._scene.setSceneRect(self._pixmap_item.boundingRect())
        self.fit_to_screen()

    def wheelEvent(self, event):
        if self._pixmap_item is None:
            return
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self._zoom += 1 if event.angleDelta().y() > 0 else -1
        self._zoom = max(-10, min(20, self._zoom))
        self.scale(factor, factor)

    def fit_to_screen(self):
        if self._pixmap_item is not None:
            self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
            self._zoom = 0

    def reset_zoom(self):
        self.resetTransform()
        self.fit_to_screen()


class ZoomableImagePanel(QWidget):
    def __init__(self, title, accent=theme.ACCENT_CYAN):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        header_row = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color:{accent}; font-weight:700; letter-spacing:1px; font-size:11px;")
        header_row.addWidget(title_label)
        header_row.addStretch()

        self.fit_btn = QPushButton("FIT")
        self.reset_btn = QPushButton("RESET ZOOM")
        for b in [self.fit_btn, self.reset_btn]:
            b.setStyleSheet("padding:2px 8px; font-size:10px;")
            header_row.addWidget(b)
        layout.addLayout(header_row)

        self.view = ZoomableGraphicsView()
        self.view.setMinimumHeight(220)
        self.view.setStyleSheet(f"background-color:{theme.BG_PANEL_LIGHT}; border-radius:6px; border:none;")
        layout.addWidget(self.view)

        self.fit_btn.clicked.connect(self.view.fit_to_screen)
        self.reset_btn.clicked.connect(self.view.reset_zoom)

    def set_image(self, array):
        self.view.set_array(array)
