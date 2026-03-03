from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class Holding:
    symbol: str
    quantity: float
    currency: str


@dataclass(frozen=True)
class Portfolio:
    base_currency: str
    holdings: List[Holding]


@dataclass(frozen=True)
class PriceSnapshot:
    symbol: str
    current: float
    previous: float
    currency: str
    timestamp: datetime