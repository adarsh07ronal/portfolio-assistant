import yfinance as yf
from datetime import datetime
from domain.models import PriceSnapshot
from providers.market_data_provider import MarketDataProvider


class YFinanceProvider(MarketDataProvider):

    def get_price(self, symbol: str) -> PriceSnapshot:

        ticker = yf.Ticker(symbol)
        data = ticker.history(period="5d")

        # If no data returned → unsupported symbol
        if data.empty or len(data) < 2:
            raise ValueError(f"No price data found for symbol: {symbol}")

        return PriceSnapshot(
            symbol=symbol,
            current=float(data["Close"].iloc[-1]),
            previous=float(data["Close"].iloc[-2]),
            currency=ticker.info.get("currency", "INR"),
            timestamp=datetime.utcnow()
        )