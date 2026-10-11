from app.preprocessing.image_registration import align_images


def test_align_images_returns_result_for_identical_images(synthetic_pair):
    aligned, ok, msg = align_images(synthetic_pair["before"], synthetic_pair["after"])
    assert aligned.shape == synthetic_pair["after"].shape
    assert isinstance(ok, bool)
    assert isinstance(msg, str)


def test_align_images_does_not_crash_on_blank_images():
    import numpy as np
    blank_a = np.zeros((64, 64, 3), dtype=np.uint8)
    blank_b = np.zeros((64, 64, 3), dtype=np.uint8)
    aligned, ok, msg = align_images(blank_a, blank_b)
    assert aligned is not None
