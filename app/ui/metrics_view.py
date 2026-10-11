from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from app.ui.widgets import StatCard, SectionPanel
from app.ui.charts import ConfusionMatrixCanvas
from app.dataset.dataset_manager import dataset_manager
from app.models.model_manager import model_manager
from app.models.metrics import confusion_counts, classification_metrics
from app.preprocessing.image_loader import load_image_rgb
from app.preprocessing.preprocessing import preprocess_pair
from app.utils.config import config
from app.utils import theme
import cv2
import numpy as np


class MetricsView(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("METRICS")
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        cards_row = QHBoxLayout()
        self.cards = {}
        for key, label in [("accuracy", "ACCURACY"), ("precision", "PRECISION"), ("recall", "RECALL"),
                            ("f1_score", "F1 SCORE"), ("iou", "IoU"), ("dice", "DICE")]:
            c = StatCard(label, "--", theme.ACCENT_CYAN)
            cards_row.addWidget(c)
            self.cards[key] = c
        layout.addLayout(cards_row)

        matrix_panel = SectionPanel("CONFUSION MATRIX (TEST SET)", theme.ACCENT_PURPLE)
        self.matrix_canvas = ConfusionMatrixCanvas()
        matrix_panel.body().addWidget(self.matrix_canvas)
        layout.addWidget(matrix_panel, stretch=1)

        self.evaluate_btn = QPushButton("EVALUATE ON TEST SET")
        self.evaluate_btn.setObjectName("PrimaryButton")
        self.evaluate_btn.clicked.connect(self.evaluate)
        layout.addWidget(self.evaluate_btn)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def evaluate(self):
        if model_manager.model is None:
            model_manager.load()
        if model_manager.model is None:
            QMessageBox.warning(self, "MODEL STATUS", "No trained model available. Train a model first.")
            return

        test_ids = dataset_manager.matching_pairs("test")
        if not test_ids:
            QMessageBox.warning(self, "DATASET", "No test samples found in dataset/test/.")
            return

        image_size = config.get("image_size", 256)
        threshold = config.get("change_threshold", 0.5)
        tp = tn = fp = fn = 0

        for sample_id in test_ids[:200]:
            paths = dataset_manager.pair_paths("test", sample_id)
            if not all(k in paths for k in ("before", "after", "mask")):
                continue
            before = cv2.cvtColor(load_image_rgb(paths["before"]), cv2.COLOR_RGB2BGR)
            after = cv2.cvtColor(load_image_rgb(paths["after"]), cv2.COLOR_RGB2BGR)
            tensor, _, _ = preprocess_pair(before, after, image_size)
            pred = model_manager.model.predict(tensor, verbose=0)[0, :, :, 0]
            pred_bin = (pred >= threshold).astype(np.uint8)

            mask = cv2.imread(paths["mask"], cv2.IMREAD_GRAYSCALE)
            mask = cv2.resize(mask, (image_size, image_size), interpolation=cv2.INTER_NEAREST)
            mask_bin = (mask > 127).astype(np.uint8)

            a, b, c, d = confusion_counts(mask_bin, pred_bin)
            tp += a; tn += b; fp += c; fn += d

        metrics = classification_metrics(tp, tn, fp, fn)
        for key, card in self.cards.items():
            card.set_value(f"{metrics[key]:.4f}")
        self.matrix_canvas.plot(tp, tn, fp, fn)
        self.status_label.setText(f"Evaluated on {len(test_ids)} test samples.")
        self.app_state.last_metrics = metrics
