import sqlite3
from pathlib import Path
from datetime import datetime


class SnapshotRepository:

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    date TEXT PRIMARY KEY,
                    total_value REAL,
                    daily_pl_percent REAL
                )
            """)

    def save_snapshot(self, total_value: float, daily_pl_percent: float):
        today = datetime.utcnow().date().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO snapshots
                (date, total_value, daily_pl_percent)
                VALUES (?, ?, ?)
            """, (today, total_value, daily_pl_percent))

    def load_all(self):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT date, total_value, daily_pl_percent
                FROM snapshots
                ORDER BY date
            """).fetchall()

        return rows