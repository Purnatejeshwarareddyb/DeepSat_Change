import sqlite3
import os
import json
import threading
from app.utils.config import ROOT_DIR
from app.utils.helpers import timestamp

DB_PATH = os.path.join(ROOT_DIR, "database", "deepsat.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    before_image TEXT,
    after_image TEXT,
    model_name TEXT,
    change_percent REAL,
    num_regions INTEGER,
    confidence REAL,
    processing_time REAL,
    severity TEXT,
    mask_path TEXT,
    overlay_path TEXT,
    metrics_json TEXT
);

CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT,
    created_at TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS training_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT,
    finished_at TEXT,
    epochs INTEGER,
    batch_size INTEGER,
    learning_rate REAL,
    final_train_loss REAL,
    final_val_loss REAL,
    final_val_dice REAL,
    final_val_iou REAL,
    fit_status TEXT,
    history_json TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


class Database:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self):
        return sqlite3.connect(DB_PATH, check_same_thread=False)

    def _init_db(self):
        with self._lock:
            conn = self._connect()
            conn.executescript(SCHEMA)
            conn.commit()
            conn.close()

    def insert_analysis(self, record):
        with self._lock:
            conn = self._connect()
            conn.execute(
                """INSERT INTO analyses
                (date, before_image, after_image, model_name, change_percent, num_regions,
                 confidence, processing_time, severity, mask_path, overlay_path, metrics_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    record.get("date", timestamp()),
                    record.get("before_image", ""),
                    record.get("after_image", ""),
                    record.get("model_name", ""),
                    record.get("change_percent", 0.0),
                    record.get("num_regions", 0),
                    record.get("confidence", 0.0),
                    record.get("processing_time", 0.0),
                    record.get("severity", ""),
                    record.get("mask_path", ""),
                    record.get("overlay_path", ""),
                    json.dumps(record.get("metrics", {})),
                ),
            )
            conn.commit()
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.close()
            return new_id

    def fetch_analyses(self, limit=200):
        with self._lock:
            conn = self._connect()
            rows = conn.execute(
                "SELECT id, date, before_image, after_image, model_name, change_percent, "
                "num_regions, confidence, processing_time, severity FROM analyses "
                "ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            conn.close()
            return rows

    def fetch_analysis(self, analysis_id):
        with self._lock:
            conn = self._connect()
            row = conn.execute("SELECT * FROM analyses WHERE id=?", (analysis_id,)).fetchone()
            conn.close()
            return row

    def delete_analysis(self, analysis_id):
        with self._lock:
            conn = self._connect()
            conn.execute("DELETE FROM analyses WHERE id=?", (analysis_id,))
            conn.commit()
            conn.close()

    def insert_training_run(self, record):
        with self._lock:
            conn = self._connect()
            conn.execute(
                """INSERT INTO training_runs
                (started_at, finished_at, epochs, batch_size, learning_rate,
                 final_train_loss, final_val_loss, final_val_dice, final_val_iou,
                 fit_status, history_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    record.get("started_at", ""),
                    record.get("finished_at", ""),
                    record.get("epochs", 0),
                    record.get("batch_size", 0),
                    record.get("learning_rate", 0.0),
                    record.get("final_train_loss", 0.0),
                    record.get("final_val_loss", 0.0),
                    record.get("final_val_dice", 0.0),
                    record.get("final_val_iou", 0.0),
                    record.get("fit_status", ""),
                    json.dumps(record.get("history", {})),
                ),
            )
            conn.commit()
            conn.close()

    def fetch_training_runs(self, limit=50):
        with self._lock:
            conn = self._connect()
            rows = conn.execute(
                "SELECT id, started_at, finished_at, epochs, final_val_loss, "
                "final_val_dice, final_val_iou, fit_status FROM training_runs "
                "ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            conn.close()
            return rows

    def latest_training_history(self):
        with self._lock:
            conn = self._connect()
            row = conn.execute(
                "SELECT history_json FROM training_runs ORDER BY id DESC LIMIT 1"
            ).fetchone()
            conn.close()
            if row and row[0]:
                return json.loads(row[0])
            return None

    def dashboard_stats(self):
        with self._lock:
            conn = self._connect()
            total = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
            changes = conn.execute("SELECT COUNT(*) FROM analyses WHERE change_percent > 0").fetchone()[0]
            avg_change = conn.execute("SELECT AVG(change_percent) FROM analyses").fetchone()[0]
            conn.close()
            return {
                "total_analyses": total,
                "changes_detected": changes,
                "average_change": avg_change if avg_change is not None else 0.0,
            }


db = Database()
