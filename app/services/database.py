# Review: This module provides functions to initialize a SQLite database, it allows saving detection entries and retrieving the history of detections. This part might be connected with the history endpoint in the API. It looks good and modular. Please, provide proper code documentation.

import sqlite3
from datetime import datetime
import json

DB_PATH = "data/detections.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_type TEXT,
            filename TEXT,
            detections TEXT,
            prompt TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_entry(entry_type: str, filename: str, detections: dict | list, prompt: str | None = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO detections (entry_type, filename, detections, prompt, timestamp) VALUES (?, ?, ?, ?, ?)",
        (entry_type, filename, json.dumps(detections), prompt, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, entry_type, filename, detections, prompt, timestamp FROM detections ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "type": r[1],
            "filename": r[2],
            "detections": json.loads(r[3]),
            "prompt": r[4],
            "timestamp": r[5]
        }
        for r in rows
    ]
