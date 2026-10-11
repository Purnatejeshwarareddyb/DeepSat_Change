import numpy as np


def compose_grid(feature_maps, columns=4, padding=2, pad_value=20):
    if not feature_maps:
        return None
    h, w = feature_maps[0].shape
    rows = (len(feature_maps) + columns - 1) // columns
    grid_h = rows * h + (rows + 1) * padding
    grid_w = columns * w + (columns + 1) * padding
    grid = np.full((grid_h, grid_w), pad_value, dtype=np.uint8)
    for idx, fmap in enumerate(feature_maps):
        r, c = divmod(idx, columns)
        y = padding + r * (h + padding)
        x = padding + c * (w + padding)
        grid[y:y + h, x:x + w] = fmap
    return grid
