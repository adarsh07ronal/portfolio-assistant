import pandas as pd
from domain.models import Portfolio, Holding


class ZerodhaExcelProvider:

    def load_portfolio(self, file_path: str, base_currency: str = "INR") -> Portfolio:

        df = pd.read_excel(file_path, header=None)

        # Dynamically find header row
        header_row = None

        for i, row in df.iterrows():
            if row.astype(str).str.contains("Symbol", case=False).any():
                header_row = i
                break

        if header_row is None:
            raise ValueError("Could not locate header row containing 'Symbol'")

        df = pd.read_excel(file_path, header=header_row)

        holdings = []

        for _, row in df.iterrows():

            symbol = str(row.get("Symbol"))

            if pd.isna(symbol):
                continue

            # Skip Sovereign Gold Bonds
            if "-GB" in symbol:
                continue

            # Clean Zerodha symbol for Yahoo
            clean_symbol = symbol.replace("-", "")

            holdings.append(
                Holding(
                    symbol=f"{clean_symbol}.NS",
                    quantity=float(row["Quantity Available"]),
                    currency="INR"
                )
            )
        return Portfolio(
            base_currency=base_currency,
            holdings=holdings
        )