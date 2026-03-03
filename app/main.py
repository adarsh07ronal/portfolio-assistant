import json
import requests
import os
from pathlib import Path

from providers.yfinance_provider import YFinanceProvider
from providers.yfinance_fx_provider import YFinanceFXProvider
from providers.zerodha_excel_provider import ZerodhaExcelProvider
from providers.benchmark_provider import BenchmarkProvider

from services.valuation_service import ValuationService
from services.performance_service import PerformanceService

from infrastructure.cache import SnapshotCache


BASE_DIR = Path(__file__).resolve().parent.parent



def send_telegram(message):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    requests.post(url, data=payload)

# ---------------------------------------------------
# Load Portfolio
# ---------------------------------------------------
def load_portfolio():
    provider = ZerodhaExcelProvider()

    file_path = BASE_DIR / "data" / "holdings.xlsx"

    if not file_path.exists():
        raise FileNotFoundError(f"Holdings file not found at {file_path}")

    return provider.load_portfolio(
        file_path=str(file_path),
        base_currency="INR"
    )


# ---------------------------------------------------
# Main
# ---------------------------------------------------
def main():
    print("🚀 Starting portfolio valuation...\n")

    portfolio = load_portfolio()

    price_provider = YFinanceProvider()
    fx_provider = YFinanceFXProvider()
    benchmark_provider = BenchmarkProvider()

    valuation_service = ValuationService()
    performance_service = PerformanceService()
    cache = SnapshotCache()

    price_map = {}
    fx_map = {}

    # ---------------------------------------------------
    # 1️⃣ Fetch Prices (safe)
    # ---------------------------------------------------
    for holding in portfolio.holdings:
        try:
            snapshot = price_provider.get_price(holding.symbol)
            price_map[holding.symbol] = snapshot
        except Exception as e:
            print(f"⚠️ Skipping {holding.symbol}: {e}")

    # Filter holdings with valid prices
    valid_holdings = [
        h for h in portfolio.holdings
        if h.symbol in price_map
    ]

    # Create NEW portfolio object (important if dataclass is frozen)
    from domain.models import Portfolio
    portfolio = Portfolio(
        base_currency=portfolio.base_currency,
        holdings=valid_holdings
    )

    # ---------------------------------------------------
    # 2️⃣ Fetch FX rates
    # ---------------------------------------------------
    currencies = {h.currency for h in portfolio.holdings}

    for currency in currencies:
        if currency == portfolio.base_currency:
            fx_map[(currency, portfolio.base_currency)] = 1.0
        else:
            rate = fx_provider.get_rate(currency, portfolio.base_currency)
            fx_map[(currency, portfolio.base_currency)] = rate

    # ---------------------------------------------------
    # 3️⃣ Value Portfolio
    # ---------------------------------------------------
    result = valuation_service.value_portfolio(
        portfolio,
        price_map,
        fx_map
    )

    # Save snapshot
    cache.save(result)

    # ---------------------------------------------------
    # 4️⃣ Performance Metrics
    # ---------------------------------------------------
    snapshots = cache.load()
    print("TYPE:", type(snapshots))
    print("VALUE:", snapshots)
    portfolio_returns = performance_service.compute_returns(snapshots)

    result["annualized_volatility"] = performance_service.annualized_volatility(snapshots)
    result["max_drawdown"] = performance_service.max_drawdown(snapshots)
    result["sharpe_ratio"] = performance_service.sharpe_ratio(snapshots)

    # ---------------------------------------------------
    # 5️⃣ Benchmark Comparison (NIFTY 50)
    # ---------------------------------------------------
    if len(snapshots) > 1:
        start_date = snapshots[0][0]
        nifty_returns = benchmark_provider.get_returns("^NSEI", start_date)
        benchmark_returns = benchmark_provider.get_returns(
    "^NSEI",
    start_date="2024-01-01"
)
        benchmark_metrics = performance_service.benchmark_analysis(
            portfolio_returns,
            benchmark_returns
        )
        beta = performance_service.beta(portfolio_returns, nifty_returns)
        alpha = performance_service.alpha(portfolio_returns, nifty_returns)
        result.update(benchmark_metrics)
        result["beta_vs_nifty"] = beta
        result["alpha_vs_nifty"] = alpha
    else:
        result["beta_vs_nifty"] = 0.0
        result["alpha_vs_nifty"] = 0.0

    # ---------------------------------------------------
    # 6️⃣ Print Result
    # ---------------------------------------------------
    print("\n📊 Portfolio Valuation Result:\n")
    print(json.dumps(result, indent=2))
    send_telegram(result)


# ---------------------------------------------------
# Entry Point
# ---------------------------------------------------
if __name__ == "__main__":
    main()