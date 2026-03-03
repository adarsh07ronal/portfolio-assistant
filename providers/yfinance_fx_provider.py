import yfinance as yf
from providers.fx_provider import FXProvider
from providers.base_market_data_provider import MarketDataProvider



class YFinanceProvider(MarketDataProvider):

    def get_price(self, symbol: str):
        data = yf.download(symbol, period="1d", progress=False)

        if data.empty:
            raise ValueError(f"No data found for {symbol}")

        return float(data["Close"].iloc[-1])