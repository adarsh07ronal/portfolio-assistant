import sqlite3
from datetime import datetime
from pathlib import Path
from domain.snapshot import Snapshot
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "portfolio.db"



class SnapshotCache:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_table()
        print("DB PATH:", DB_PATH)

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_value REAL NOT NULL,
                daily_pl_percent REAL
            )
        """)
        self.conn.commit()

    def save(self, result):
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if today's snapshot already exists
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM snapshots WHERE date = ?",
            (today,)
        )

        exists = cursor.fetchone()[0]

        if exists:
            return  # Do not insert duplicate

        self.conn.execute("""
            INSERT INTO snapshots (date, total_value, daily_pl_percent)
            VALUES (?, ?, ?)
        """, (
            today,
            float(result["total_value"]),
            float(result.get("daily_pl_percent", 0.0))
        ))

        self.conn.commit()



    def load(self):
        rows = self.conn.execute(
            "SELECT date, total_value, daily_pl_percent FROM snapshots ORDER BY date"
        ).fetchall()

        snapshots = []

        for row in rows:
            snapshots.append(
                Snapshot(
                    date=datetime.strptime(row[0], "%Y-%m-%d").date(),
                    total_value=row[1],
                    daily_pl_percent=row[2]
                )
            )

        return snapshots