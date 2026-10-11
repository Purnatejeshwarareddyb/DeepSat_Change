from app.utils.helpers import fit_analysis, severity_label


def test_fit_analysis_insufficient_data_below_minimum_epochs():
    assert fit_analysis([0.5, 0.4], [0.5, 0.4]) == "INSUFFICIENT DATA"


def test_fit_analysis_good_fit_when_noisy_but_both_improving():
    train = [0.47 - 0.005 * i for i in range(27)]
    noisy_offsets = [0.0, 0.02, -0.01, 0.05, -0.03, 0.01, 0.04, -0.02, 0.0, 0.03,
                      -0.01, 0.02, 0.0, -0.02, 0.01, 0.03, -0.01, 0.0, 0.02, -0.03,
                      0.01, 0.05, -0.02, 0.0, 0.01, -0.01, 0.02]
    val = [max(0.33, 0.50 - 0.004 * i + noisy_offsets[i]) for i in range(27)]
    assert fit_analysis(train, val) == "GOOD FIT"


def test_fit_analysis_detects_genuine_overfitting():
    train = [0.5 - 0.015 * i for i in range(20)]
    val = [0.45 - 0.01 * i if i < 8 else 0.37 + 0.01 * (i - 8) for i in range(20)]
    assert fit_analysis(train, val) == "POSSIBLE OVERFITTING"


def test_fit_analysis_detects_genuine_underfitting():
    train = [0.6] * 20
    val = [0.62] * 20
    assert fit_analysis(train, val) == "POSSIBLE UNDERFITTING"


def test_fit_analysis_good_fit_when_both_improve_together():
    train = [0.5 - 0.012 * i for i in range(20)]
    val = [0.52 - 0.011 * i for i in range(20)]
    assert fit_analysis(train, val) == "GOOD FIT"


def test_severity_label_boundaries():
    assert severity_label(0) == "VERY LOW"
    assert severity_label(4.9) == "VERY LOW"
    assert severity_label(5) == "LOW"
    assert severity_label(14.9) == "LOW"
    assert severity_label(15) == "MODERATE"
    assert severity_label(29.9) == "MODERATE"
    assert severity_label(30) == "HIGH"
    assert severity_label(49.9) == "HIGH"
    assert severity_label(50) == "VERY HIGH"
