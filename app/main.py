import json
from pathlib import Path

from providers.yfinance_provider import YFinanceProvider
from providers.benchmark_provider import BenchmarkProvider
from providers.zerodha_excel_provider import ZerodhaExcelProvider
from infrastructure.telegram_notifier import TelegramNotifier
from infrastructure.cache import SnapshotCache
from services.alert_service import AlertService
from services.valuation_service import ValuationService
from services.performance_service import PerformanceService


BASE_DIR = Path(__file__).resolve().parent.parent


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
    benchmark_provider = BenchmarkProvider()
    valuation_service = ValuationService()
    performance_service = PerformanceService()
    cache = SnapshotCache()
    notifier = TelegramNotifier()
    alert_service = AlertService()

    price_map = {}
    fx_map = {}

    # 1️⃣ Fetch Prices
    for holding in portfolio.holdings:
        try:
            price = price_provider.get_price(holding.symbol)
            price_map[holding.symbol] = price
        except Exception as e:
            print(f"⚠️ Skipping {holding.symbol}: {e}")

    # 2️⃣ FX (simple INR-only assumption)
    for holding in portfolio.holdings:
        fx_map[(holding.currency, portfolio.base_currency)] = 1.0

    # 3️⃣ Value Portfolio
    result = valuation_service.value_portfolio(
        portfolio,
        price_map,
        fx_map
    )

    # Save snapshot
    cache.save(result)

    # 4️⃣ Performance
    snapshots = cache.load()

    portfolio_returns = performance_service.compute_returns(snapshots)

    result["annualized_volatility"] = performance_service.annualized_volatility(snapshots)
    result["max_drawdown"] = performance_service.max_drawdown(snapshots)
    result["sharpe_ratio"] = performance_service.sharpe_ratio(snapshots)

    # 5️⃣ Benchmark Comparison
    if len(snapshots) > 1:
        start_date = snapshots[0].date

        benchmark_returns = benchmark_provider.get_returns(
            "^NSEI",
            start_date=start_date
        )

        benchmark_metrics = performance_service.benchmark_analysis(
            portfolio_returns,
            benchmark_returns
        )

        result.update(benchmark_metrics)

    else:
        result["beta_vs_nifty"] = 0.0
        result["alpha_vs_nifty"] = 0.0
        result["correlation_vs_nifty"] = 0.0
        result["tracking_error"] = 0.0

    # 6️⃣ Send Telegram
    message = alert_service.build_summary_message(result)

    print("\n📊 Portfolio Valuation Result:\n")
    print(json.dumps(result, indent=2))

    notifier.send(message)


# ---------------------------------------------------
# Entry Point
# ---------------------------------------------------
if __name__ == "__main__":
    main()