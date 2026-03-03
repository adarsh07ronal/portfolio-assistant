from abc import ABC, abstractmethod
from domain.models import PriceSnapshot


class MarketDataProvider(ABC):

    @abstractmethod
    def get_price(self, symbol: str) -> PriceSnapshot:
        pass