import json
import os
from app.utils.config import ROOT_DIR
from app.utils.helpers import ensure_dir, timestamp

HISTORY_DIR = ensure_dir(os.path.join(ROOT_DIR, "logs", "training_history"))


def save_run(history_dict, fit_status, run_config):
    ensure_dir(HISTORY_DIR)
    filename = f"run_{timestamp().replace(':', '-').replace(' ', '_')}.json"
    path = os.path.join(HISTORY_DIR, filename)
    payload = {
        "config": run_config,
        "fit_status": fit_status,
        "history": history_dict,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path


def load_all_runs():
    if not os.path.isdir(HISTORY_DIR):
        return []
    runs = []
    for fname in sorted(os.listdir(HISTORY_DIR)):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(HISTORY_DIR, fname), "r") as f:
                    runs.append(json.load(f))
            except (json.JSONDecodeError, OSError):
                continue
    return runs


def load_latest_run():
    runs = load_all_runs()
    return runs[-1] if runs else None
