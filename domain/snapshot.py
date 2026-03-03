from dataclasses import dataclass
from datetime import date


@dataclass
class Snapshot:
    date: date
    total_value: float
    daily_pl_percent: float