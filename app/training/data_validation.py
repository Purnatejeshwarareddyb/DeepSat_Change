MIN_SAMPLES_PER_SPLIT = 1


class DatasetTrainingError(Exception):
    pass


def validate_for_training(dataset_manager):
    report = dataset_manager.validation_report()
    train_report = report.get("train", {})
    if train_report.get("matching_pairs", 0) < MIN_SAMPLES_PER_SPLIT:
        raise DatasetTrainingError(
            "No matching training samples found. Use the Dataset Manager to "
            "validate or select a dataset with before/after/mask triplets."
        )

    val_report = report.get("validation", {})
    test_report = report.get("test", {})
    val_available = val_report.get("matching_pairs", 0) > 0
    test_available = test_report.get("matching_pairs", 0) > 0

    if not val_available and not test_available:
        return {
            "train_count": train_report["matching_pairs"],
            "val_count": 0,
            "val_source": "held_out_from_train",
            "warning": "No validation or test split found. A portion of the training "
                       "set will be held out for validation.",
        }

    val_source = "validation" if val_available else "test"
    val_count = val_report["matching_pairs"] if val_available else test_report["matching_pairs"]
    return {
        "train_count": train_report["matching_pairs"],
        "val_count": val_count,
        "val_source": val_source,
        "warning": None,
    }
