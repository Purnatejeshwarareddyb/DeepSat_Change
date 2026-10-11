import numpy as np
from app.preprocessing.image_validator import validate_image, validate_pair
from app.preprocessing.preprocessing import preprocess_pair, resize_to_match
from app.preprocessing.augmentation import augment_triplet


def test_validate_image_accepts_valid_file(synthetic_pair):
    result = validate_image(synthetic_pair["before_path"])
    assert result.is_valid


def test_validate_image_rejects_missing_file():
    result = validate_image("/nonexistent/path.png")
    assert not result.is_valid


def test_validate_pair_matching_dimensions(synthetic_pair):
    result = validate_pair(synthetic_pair["before_path"], synthetic_pair["after_path"])
    assert result.is_valid


def test_preprocess_pair_produces_correct_tensor_shape(synthetic_pair):
    tensor, before_r, after_r = preprocess_pair(synthetic_pair["before"], synthetic_pair["after"], 64)
    assert tensor.shape == (1, 64, 64, 6)
    assert tensor.min() >= 0.0 and tensor.max() <= 1.0
    assert before_r.shape == (64, 64, 3)


def test_resize_to_match_handles_mismatched_sizes():
    a = np.zeros((100, 120, 3), dtype=np.uint8)
    b = np.zeros((80, 90, 3), dtype=np.uint8)
    ar, br = resize_to_match(a, b)
    assert ar.shape == br.shape


def test_augment_triplet_preserves_shapes(synthetic_pair):
    before, after, mask = augment_triplet(synthetic_pair["before"], synthetic_pair["after"], synthetic_pair["mask"])
    assert before.shape == synthetic_pair["before"].shape or before.shape[:2] == synthetic_pair["before"].shape[:2][::-1]
    assert after.shape[:2] == before.shape[:2]
    assert mask.shape[:2] == before.shape[:2]
