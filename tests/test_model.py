import numpy as np
from app.models.unet import build_lightweight_unet, count_parameters
from app.models.losses import bce_dice_loss, dice_loss
from app.models.metrics import iou_metric, dice_metric


def test_build_lightweight_unet_output_shape():
    model = build_lightweight_unet(input_size=64, in_channels=6, base_filters=8)
    assert model.input_shape == (None, 64, 64, 6)
    assert model.output_shape == (None, 64, 64, 1)


def test_count_parameters_returns_positive_counts():
    model = build_lightweight_unet(input_size=64, in_channels=6, base_filters=8)
    total, trainable = count_parameters(model)
    assert total > 0
    assert trainable > 0
    assert trainable <= total


def test_model_predicts_probabilities_between_zero_and_one():
    model = build_lightweight_unet(input_size=64, in_channels=6, base_filters=8)
    x = np.random.rand(1, 64, 64, 6).astype("float32")
    pred = model.predict(x, verbose=0)
    assert pred.min() >= 0.0 and pred.max() <= 1.0


def test_dice_loss_is_zero_for_perfect_match():
    import tensorflow as tf
    y = tf.ones((1, 8, 8, 1))
    loss = dice_loss(y, y)
    assert float(loss) < 1e-3


def test_bce_dice_loss_runs_without_error():
    import tensorflow as tf
    y_true = tf.random.uniform((2, 8, 8, 1)) > 0.5
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.random.uniform((2, 8, 8, 1))
    loss_fn = bce_dice_loss()
    value = loss_fn(y_true, y_pred)
    assert float(value) >= 0.0
