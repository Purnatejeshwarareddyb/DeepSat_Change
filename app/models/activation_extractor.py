import numpy as np
import tensorflow as tf


def get_conv_layer_names(model):
    return [layer.name for layer in model.layers if isinstance(layer, tf.keras.layers.Conv2D)]


def extract_feature_maps(model, tensor, layer_name, max_maps=16):
    target_layer = model.get_layer(layer_name)
    activation_model = tf.keras.Model(inputs=model.inputs, outputs=target_layer.output)
    activations = activation_model.predict(tensor, verbose=0)[0]
    num_maps = min(max_maps, activations.shape[-1])
    maps = []
    for i in range(num_maps):
        fmap = activations[:, :, i]
        fmin, fmax = fmap.min(), fmap.max()
        normalized = (fmap - fmin) / (fmax - fmin + 1e-8)
        maps.append((normalized * 255).astype(np.uint8))
    return maps
