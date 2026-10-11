import numpy as np
import matplotlib


def probability_to_heatmap(probability_map, colormap="inferno"):
    try:
        cmap = matplotlib.colormaps[colormap]
    except (AttributeError, KeyError):
        import matplotlib.cm as cm
        cmap = cm.get_cmap(colormap)
    colored = cmap(probability_map)[:, :, :3]
    return (colored * 255).astype(np.uint8)
