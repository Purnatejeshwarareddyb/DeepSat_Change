import os
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from app.visualization.image_viewer import ZoomableGraphicsView
from app.models.model_manager import model_manager
from app.models.activation_extractor import get_conv_layer_names, extract_feature_maps
from app.utils.config import ROOT_DIR
from app.utils.helpers import ensure_dir, timestamp
from app.utils import theme


class FeatureMapTile(QWidget):
    def __init__(self, title, array):
        super().__init__()
        self.array = array
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        label = QLabel(title)
        label.setStyleSheet(f"color:{theme.ACCENT_PURPLE}; font-weight:700; font-size:10px; letter-spacing:1px;")
        layout.addWidget(label)

        self.view = ZoomableGraphicsView()
        self.view.setMinimumSize(180, 180)
        self.view.setStyleSheet(f"background-color:{theme.BG_PANEL_LIGHT}; border-radius:6px; border:none;")
        upscaled = cv2.resize(array, (256, 256), interpolation=cv2.INTER_NEAREST)
        self.view.set_array(upscaled)
        layout.addWidget(self.view)


class ActivationMapsView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.current_maps = []
        self.current_layer_name = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("ACTIVATION MAPS")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        note = QLabel("Feature maps are shown at native resolution with sharp (nearest-neighbor) scaling "
                       "and can be zoomed. Deeper encoder layers produce smaller, more abstract maps.")
        note.setWordWrap(True)
        note.setStyleSheet(f"color:{theme.TEXT_SECONDARY}; font-size:11px;")
        layout.addWidget(note)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("ENCODER LAYER"))
        self.layer_combo = QComboBox()
        controls.addWidget(self.layer_combo)
        self.generate_btn = QPushButton("GENERATE FEATURE MAPS")
        self.generate_btn.setObjectName("PrimaryButton")
        controls.addWidget(self.generate_btn)
        self.save_btn = QPushButton("SAVE FEATURE MAPS")
        controls.addWidget(self.save_btn)
        layout.addLayout(controls)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll, stretch=1)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color:{theme.TEXT_SECONDARY};")
        layout.addWidget(self.status_label)

        self.generate_btn.clicked.connect(self.generate_maps)
        self.save_btn.clicked.connect(self.save_maps)

    def refresh_layers(self):
        self.layer_combo.clear()
        if model_manager.model is not None:
            self.layer_combo.addItems(get_conv_layer_names(model_manager.model))

    def generate_maps(self):
        if model_manager.model is None:
            QMessageBox.warning(self, "MODEL STATUS", "Load or train a model first.")
            return
        if self.app_state.preprocessed_tensor is None:
            QMessageBox.warning(self, "ERROR", "Run preprocessing on an image pair first (Preprocessing page).")
            return
        layer_name = self.layer_combo.currentText()
        if not layer_name:
            return

        self.current_layer_name = layer_name
        self.current_maps = extract_feature_maps(model_manager.model, self.app_state.preprocessed_tensor, layer_name)

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        cols = 4
        for idx, fmap in enumerate(self.current_maps):
            tile = FeatureMapTile(f"MAP {idx + 1}", fmap)
            self.grid_layout.addWidget(tile, idx // cols, idx % cols)

        self.status_label.setText(f"Generated {len(self.current_maps)} feature maps from layer '{layer_name}'.")

    def save_maps(self):
        if not self.current_maps:
            QMessageBox.warning(self, "ERROR", "Generate feature maps first.")
            return
        out_dir = ensure_dir(os.path.join(ROOT_DIR, "results", "activation_maps"))
        stamp = timestamp().replace(':', '-').replace(' ', '_')
        saved = 0
        for idx, fmap in enumerate(self.current_maps):
            upscaled = cv2.resize(fmap, (256, 256), interpolation=cv2.INTER_NEAREST)
            path = os.path.join(out_dir, f"{self.current_layer_name}_{stamp}_map{idx + 1:02d}.png")
            cv2.imwrite(path, upscaled)
            saved += 1
        self.status_label.setText(f"Saved {saved} feature map images to results/activation_maps/")
