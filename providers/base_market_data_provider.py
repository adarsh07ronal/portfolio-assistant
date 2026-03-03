from abc import ABC, abstractmethod


class MarketDataProvider(ABC):

    @abstractmethod
    def get_price(self, symbol: str):
        """Return latest price snapshot for a symbol"""
        pass