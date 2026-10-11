import os
import time


def human_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def severity_label(change_percent):
    if change_percent < 5:
        return "VERY LOW"
    if change_percent < 15:
        return "LOW"
    if change_percent < 30:
        return "MODERATE"
    if change_percent < 50:
        return "HIGH"
    return "VERY HIGH"


def fit_analysis(train_losses, val_losses, min_gap=0.03, min_improvement=0.01):
    n = len(train_losses)
    if n < 6 or len(val_losses) < 6:
        return "INSUFFICIENT DATA"

    window = max(2, min(5, n // 3))
    train_early = sum(train_losses[:window]) / window
    train_recent = sum(train_losses[-window:]) / window
    val_early = sum(val_losses[:window]) / window
    val_recent = sum(val_losses[-window:]) / window

    train_improved = (train_early - train_recent) > min_improvement
    val_improved = (val_early - val_recent) > min_improvement
    gap_early = val_early - train_early
    gap_recent = val_recent - train_recent
    gap_widened = (gap_recent - gap_early) > min_gap

    if train_improved and gap_widened and not val_improved:
        return "POSSIBLE OVERFITTING"
    if not train_improved and not val_improved:
        return "POSSIBLE UNDERFITTING"
    return "GOOD FIT"
