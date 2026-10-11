import json


def export_analysis_json(metadata, metrics, regions, path):
    payload = {
        "metadata": metadata,
        "metrics": metrics,
        "regions": regions,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path
