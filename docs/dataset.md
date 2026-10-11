# Dataset Format

dataset/{train,validation,test}/{before,after,mask}/<id>.<ext>

before/after: RGB satellite images of the same region at two time points.
mask: single-channel image, 255 = changed pixel, 0 = unchanged.
Filenames (without extension) must match across before/after/mask.
