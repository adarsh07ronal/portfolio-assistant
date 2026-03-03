import yfinance as yf
from providers.fx_provider import FXProvider


class YFinanceFXProvider(FXProvider):

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return 1.0

        pair = f"{from_currency}{to_currency}=X"
        data = yf.Ticker(pair).history(period="1d")

        return float(data["Close"].iloc[-1])