import tensorflow as tf
from tensorflow.keras import layers, Model


def conv_block(x, filters):
    x = layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    return x


def build_lightweight_unet(input_size=256, in_channels=6, base_filters=16):
    inputs = layers.Input(shape=(input_size, input_size, in_channels), name="before_after_concat")

    c1 = conv_block(inputs, base_filters)
    p1 = layers.MaxPooling2D()(c1)

    c2 = conv_block(p1, base_filters * 2)
    p2 = layers.MaxPooling2D()(c2)

    c3 = conv_block(p2, base_filters * 4)
    p3 = layers.MaxPooling2D()(c3)

    c4 = conv_block(p3, base_filters * 8)
    p4 = layers.MaxPooling2D()(c4)

    b = conv_block(p4, base_filters * 16)

    u4 = layers.Conv2DTranspose(base_filters * 8, 2, strides=2, padding="same")(b)
    u4 = layers.Concatenate()([u4, c4])
    u4 = conv_block(u4, base_filters * 8)

    u3 = layers.Conv2DTranspose(base_filters * 4, 2, strides=2, padding="same")(u4)
    u3 = layers.Concatenate()([u3, c3])
    u3 = conv_block(u3, base_filters * 4)

    u2 = layers.Conv2DTranspose(base_filters * 2, 2, strides=2, padding="same")(u3)
    u2 = layers.Concatenate()([u2, c2])
    u2 = conv_block(u2, base_filters * 2)

    u1 = layers.Conv2DTranspose(base_filters, 2, strides=2, padding="same")(u2)
    u1 = layers.Concatenate()([u1, c1])
    u1 = conv_block(u1, base_filters)

    outputs = layers.Conv2D(1, 1, activation="sigmoid", name="change_mask")(u1)

    return Model(inputs, outputs, name="lightweight_unet_change_detection")


def count_parameters(model):
    trainable = int(sum(tf.keras.backend.count_params(w) for w in model.trainable_weights))
    total = int(sum(tf.keras.backend.count_params(w) for w in model.weights))
    return total, trainable
