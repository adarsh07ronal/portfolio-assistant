from dataclasses import dataclass


@dataclass
class PortfolioResult:
    total_value: float
    daily_pl_percent: float
    sharpe_ratio: float = 0.0
    annualized_volatility: float = 0.0
    max_drawdown: float = 0.0
    beta_vs_nifty: float = 0.0
    alpha_vs_nifty: float = 0.0