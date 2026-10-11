import tensorflow as tf


def dice_loss(y_true, y_pred, smooth=1e-6):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    intersection = tf.reduce_sum(y_true * y_pred, axis=[1, 2, 3])
    union = tf.reduce_sum(y_true, axis=[1, 2, 3]) + tf.reduce_sum(y_pred, axis=[1, 2, 3])
    dice = (2.0 * intersection + smooth) / (union + smooth)
    return 1.0 - tf.reduce_mean(dice)


def bce_dice_loss(bce_weight=0.5, dice_weight=0.5):
    bce = tf.keras.losses.BinaryCrossentropy()

    def loss_fn(y_true, y_pred):
        return bce_weight * bce(y_true, y_pred) + dice_weight * dice_loss(y_true, y_pred)

    loss_fn.__name__ = "bce_dice_loss"
    return loss_fn
