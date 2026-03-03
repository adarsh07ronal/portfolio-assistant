class AlertService:

    def build_summary_message(self, result: dict) -> str:
        message = "📊 Portfolio Update\n\n"
        message += f"💰 Total Value: ₹{result['total_value']:,.0f}\n"
        message += f"📉 Daily P&L: {result['daily_pl_percent']:.2f}%\n"
        message += f"📈 Sharpe: {result.get('sharpe_ratio', 0):.2f}\n"
        message += f"⚡ Volatility: {result.get('annualized_volatility', 0):.2f}\n"
        message += f"📉 Max Drawdown: {result.get('max_drawdown', 0):.2%}\n"
        message += f"📊 Beta vs NIFTY: {result.get('beta_vs_nifty', 0):.2f}\n"
        message += f"🔥 Alpha vs NIFTY: {result.get('alpha_vs_nifty', 0):.2f}\n"

        alerts = self._generate_alerts(result)

        if alerts:
            message += "\n🚨 Alerts:\n"
            for alert in alerts:
                message += f"- {alert}\n"

        return message

    def _generate_alerts(self, result: dict):
        alerts = []

        if result.get("max_drawdown", 0) < -0.05:
            alerts.append("Drawdown exceeded 5%")

        if result.get("beta_vs_nifty", 0) > 1.2:
            alerts.append("High Beta vs NIFTY")

        if result.get("annualized_volatility", 0) > 0.20:
            alerts.append("High Volatility")

        if result.get("daily_pl_percent", 0) < -2:
            alerts.append("Daily loss > 2%")

        return alerts