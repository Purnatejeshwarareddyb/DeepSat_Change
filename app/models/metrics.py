import numpy as np
import tensorflow as tf


def iou_metric(y_true, y_pred, threshold=0.5, smooth=1e-6):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(tf.cast(y_pred > threshold, tf.float32), tf.float32)
    intersection = tf.reduce_sum(y_true * y_pred, axis=[1, 2, 3])
    union = tf.reduce_sum(y_true, axis=[1, 2, 3]) + tf.reduce_sum(y_pred, axis=[1, 2, 3]) - intersection
    return tf.reduce_mean((intersection + smooth) / (union + smooth))


def dice_metric(y_true, y_pred, threshold=0.5, smooth=1e-6):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(tf.cast(y_pred > threshold, tf.float32), tf.float32)
    intersection = tf.reduce_sum(y_true * y_pred, axis=[1, 2, 3])
    total = tf.reduce_sum(y_true, axis=[1, 2, 3]) + tf.reduce_sum(y_pred, axis=[1, 2, 3])
    return tf.reduce_mean((2.0 * intersection + smooth) / (total + smooth))


def confusion_counts(y_true_bin, y_pred_bin):
    y_true_bin = y_true_bin.astype(bool).flatten()
    y_pred_bin = y_pred_bin.astype(bool).flatten()
    tp = int(np.sum(y_true_bin & y_pred_bin))
    tn = int(np.sum(~y_true_bin & ~y_pred_bin))
    fp = int(np.sum(~y_true_bin & y_pred_bin))
    fn = int(np.sum(y_true_bin & ~y_pred_bin))
    return tp, tn, fp, fn


def classification_metrics(tp, tn, fp, fn, eps=1e-9):
    accuracy = (tp + tn) / (tp + tn + fp + fn + eps)
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    f1 = 2 * precision * recall / (precision + recall + eps)
    iou = tp / (tp + fp + fn + eps)
    dice = 2 * tp / (2 * tp + fp + fn + eps)
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "iou": float(iou),
        "dice": float(dice),
    }
