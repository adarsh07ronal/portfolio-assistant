import yfinance as yf
import pandas as pd


class BenchmarkProvider:

    def get_returns(self, symbol="^NSEI", start_date="2024-01-01"):
        data = yf.download(symbol, start=start_date, progress=False)

        if data.empty:
            return pd.Series(dtype=float)

        returns = data["Close"].pct_change().dropna()

        return returns