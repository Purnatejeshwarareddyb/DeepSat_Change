import os
import json
from app.reports.csv_export import export_regions_csv
from app.reports.json_export import export_analysis_json
from app.reports.pdf_report import generate_report


REGIONS = [{"region_id": 1, "area": 900, "width": 30, "height": 30,
            "centroid": [35, 35], "relative_area": 9.0, "bbox": [20, 20, 30, 30]}]
STATS = {"change_percent": 9.0, "severity": "LOW", "total_pixels": 10000,
         "changed_pixels": 900, "confidence": 0.88}
METRICS = {"iou": 0.84, "dice": 0.91, "precision": 0.92, "recall": 0.90, "f1_score": 0.91}


def test_export_regions_csv_writes_expected_header(tmp_path):
    path = str(tmp_path / "regions.csv")
    export_regions_csv(REGIONS, path)
    content = open(path).read()
    assert "Region ID" in content
    assert "900" in content


def test_export_analysis_json_round_trips(tmp_path):
    path = str(tmp_path / "analysis.json")
    export_analysis_json({"note": "test"}, STATS, REGIONS, path)
    with open(path) as f:
        data = json.load(f)
    assert data["metrics"]["change_percent"] == 9.0
    assert data["regions"][0]["area"] == 900


def test_generate_report_creates_pdf_file(tmp_path, synthetic_pair):
    import cv2
    before_p = str(tmp_path / "before.png")
    after_p = str(tmp_path / "after.png")
    mask_p = str(tmp_path / "mask.png")
    overlay_p = str(tmp_path / "overlay.png")
    cv2.imwrite(before_p, synthetic_pair["before"])
    cv2.imwrite(after_p, synthetic_pair["after"])
    cv2.imwrite(mask_p, synthetic_pair["mask"])
    cv2.imwrite(overlay_p, synthetic_pair["after"])

    out_path = str(tmp_path / "report.pdf")
    generate_report(out_path, before_p, after_p, mask_p, overlay_p, STATS, METRICS, REGIONS, {"model_name": "Lightweight U-Net"})
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 0
