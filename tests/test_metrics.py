import numpy as np
from app.models.metrics import confusion_counts, classification_metrics


def test_confusion_counts_matches_manual_calculation():
    y_true = np.array([[1, 0], [0, 1]])
    y_pred = np.array([[1, 0], [1, 1]])
    tp, tn, fp, fn = confusion_counts(y_true, y_pred)
    assert (tp, tn, fp, fn) == (2, 1, 1, 0)


def test_classification_metrics_are_within_valid_range():
    metrics = classification_metrics(tp=8, tn=80, fp=2, fn=10)
    for key in ["accuracy", "precision", "recall", "f1_score", "iou", "dice"]:
        assert 0.0 <= metrics[key] <= 1.0


def test_classification_metrics_perfect_prediction():
    metrics = classification_metrics(tp=10, tn=90, fp=0, fn=0)
    assert round(metrics["accuracy"], 3) == 1.0
    assert round(metrics["iou"], 3) == 1.0
    assert round(metrics["dice"], 3) == 1.0
