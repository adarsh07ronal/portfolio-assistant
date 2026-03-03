from abc import ABC, abstractmethod

class FXProvider(ABC):

    @abstractmethod
    def get_rate(self, from_currency: str, to_currency: str) -> float:
        pass