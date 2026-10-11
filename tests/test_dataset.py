from app.dataset.dataset_validator import validate_dataset, validate_split


def test_validate_split_finds_matching_pairs(synthetic_dataset):
    import os
    report = validate_split(os.path.join(synthetic_dataset, "train"))
    assert report["matching_pairs"] == 6
    assert report["valid"]


def test_validate_dataset_reports_all_splits(synthetic_dataset):
    report = validate_dataset(synthetic_dataset)
    assert report["overall_valid"]
    assert report["train"]["matching_pairs"] == 6
    assert report["validation"]["matching_pairs"] == 2
    assert report["test"]["matching_pairs"] == 2


def test_validate_dataset_on_empty_folder(tmp_path):
    report = validate_dataset(str(tmp_path / "empty"))
    assert not report["overall_valid"]
