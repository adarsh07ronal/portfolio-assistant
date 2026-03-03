import pandas as pd
import numpy as np


class PerformanceService:

    # --------------------------------------------
    # Compute daily returns
    # --------------------------------------------
    def compute_returns(self, snapshots):
        if not snapshots:
            return pd.Series(dtype=float)

        dates = [s.date for s in snapshots]
        values = [s.total_value for s in snapshots]

        if len(values) < 2:
            return pd.Series(dtype=float)

        df = pd.DataFrame({"date": dates, "value": values})

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.drop_duplicates(subset="date")

        df = df.sort_values("date")
        df.set_index("date", inplace=True)

        returns = df["value"].pct_change().dropna()

        return returns

    # --------------------------------------------
    # Annualized Volatility
    # --------------------------------------------
    def annualized_volatility(self, snapshots):
        returns = self.compute_returns(snapshots)

        if len(returns) < 2:
            return 0.0

        return float(np.std(returns) * np.sqrt(252))

    # --------------------------------------------
    # Max Drawdown
    # --------------------------------------------
    def max_drawdown(self, snapshots):
        values = [s.total_value for s in snapshots]

        if len(values) < 2:
            return 0.0

        cumulative = np.array(values)
        rolling_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - rolling_max) / rolling_max

        return float(np.min(drawdowns))

    # --------------------------------------------
    # Sharpe Ratio
    # --------------------------------------------
    def sharpe_ratio(self, snapshots, risk_free_rate=0.0):
        returns = self.compute_returns(snapshots)

        if len(returns) < 2:
            return 0.0

        mean_daily_return = np.mean(returns)
        annual_return = mean_daily_return * 252

        volatility = self.annualized_volatility(snapshots)

        if volatility == 0:
            return 0.0

        sharpe = (annual_return - risk_free_rate) / volatility
        return float(sharpe)

    # --------------------------------------------
    # Beta
    # --------------------------------------------
    def beta(self, portfolio_returns, benchmark_returns):
        if portfolio_returns.empty or benchmark_returns.empty:
            return 0.0

        df = pd.concat(
            [portfolio_returns, benchmark_returns],
            axis=1,
            join="inner"
        )

        if len(df) < 2:
            return 0.0

        df.columns = ["portfolio", "benchmark"]

        cov = df.cov().iloc[0, 1]
        var = df["benchmark"].var()

        if var == 0:
            return 0.0

        return float(cov / var)

    # --------------------------------------------
    # Alpha
    # --------------------------------------------
    def alpha(self, portfolio_returns, benchmark_returns, risk_free_rate=0.0):
        beta = self.beta(portfolio_returns, benchmark_returns)

        if portfolio_returns.empty or benchmark_returns.empty:
            return 0.0

        rp = np.mean(portfolio_returns) * 252
        rm = np.mean(benchmark_returns) * 252

        alpha = rp - (risk_free_rate + beta * (rm - risk_free_rate))

        return float(alpha)

    # --------------------------------------------
    # Benchmark Analysis
    # --------------------------------------------
    def benchmark_analysis(self, portfolio_returns, benchmark_returns):

        if portfolio_returns.empty or benchmark_returns.empty:
            return {
                "beta_vs_nifty": 0.0,
                "alpha_vs_nifty": 0.0,
                "correlation_vs_nifty": 0.0,
                "tracking_error": 0.0
            }

        df = pd.concat(
            [portfolio_returns, benchmark_returns],
            axis=1,
            join="inner"
        )

        if len(df) < 2:
            return {
                "beta_vs_nifty": 0.0,
                "alpha_vs_nifty": 0.0,
                "correlation_vs_nifty": 0.0,
                "tracking_error": 0.0
            }

        df.columns = ["portfolio", "benchmark"]

        cov = df.cov().iloc[0, 1]
        var = df["benchmark"].var()
        beta = cov / var if var != 0 else 0.0

        annual_portfolio_return = df["portfolio"].mean() * 252
        annual_benchmark_return = df["benchmark"].mean() * 252

        alpha = annual_portfolio_return - beta * annual_benchmark_return

        correlation = df.corr().iloc[0, 1]

        tracking_error = (
            (df["portfolio"] - df["benchmark"]).std()
            * np.sqrt(252)
        )

        return {
            "beta_vs_nifty": float(beta),
            "alpha_vs_nifty": float(alpha),
            "correlation_vs_nifty": float(correlation),
            "tracking_error": float(tracking_error)
        }