# Architecture

Before + After RGB images are concatenated into a 6-channel tensor and fed to
a lightweight encoder-decoder U-Net. The encoder downsamples through four
conv-block + max-pool stages; the bottleneck sits at the base resolution; the
decoder upsamples via Conv2DTranspose with skip connections back to matching
encoder stages. A final 1x1 convolution with sigmoid activation produces a
per-pixel change probability map, thresholded and cleaned into a binary mask.
