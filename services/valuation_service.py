from domain.models import Portfolio, PriceSnapshot


class ValuationService:

    def value_portfolio(self, portfolio: Portfolio, price_map, fx_map):

        total_value = 0
        total_prev = 0
        allocation = {}
        fx_exposure = {}

        for holding in portfolio.holdings:

            snapshot = price_map.get(holding.symbol)

            if snapshot is None:
                continue

            fx_rate = fx_map.get(
                (holding.currency, portfolio.base_currency),
                1.0
            )

            current_value = holding.quantity * snapshot.current * fx_rate
            prev_value = holding.quantity * snapshot.previous * fx_rate

            total_value += current_value
            total_prev += prev_value

            allocation[holding.symbol] = current_value

            fx_exposure[holding.currency] = (
                fx_exposure.get(holding.currency, 0) + current_value
            )

        daily_pl_percent = (
            (total_value - total_prev) / total_prev
            if total_prev > 0 else 0
        )

        return {
            "total_value": total_value,
            "daily_pl_percent": daily_pl_percent,
            "allocation_percent": {
                k: v / total_value * 100
                for k, v in allocation.items()
            },
            "fx_exposure_percent": {
                k: v / total_value * 100
                for k, v in fx_exposure.items()
            }
        }