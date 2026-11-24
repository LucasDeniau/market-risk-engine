"""P&L quotidien du book : statistiques et pires jours."""

import pandas as pd

from riskengine.config import load_config
from riskengine.portfolio.book import option_positions
from riskengine.portfolio.pnl import daily_pnl

cfg = load_config("config/portfolio.yaml")
data = pd.read_parquet("data/processed/market_data.parquet")
pnl = daily_pnl(cfg, data, option_positions(cfg, data))

print(f"{len(pnl)} jours de P&L")
print(f"P&L moyen : {pnl['total'].mean():,.0f} EUR/jour | écart-type : {pnl['total'].std():,.0f} EUR")
print()
print("Les 5 pires jours :")
pires = pnl["total"].nsmallest(5).index
print(pnl.loc[pires, "total"].round(0))
print()
print("Mars 2020, P&L cumulé par composante (EUR) :")
mars = pnl.loc["2020-03"]
print(mars.drop(columns="total").sum().round(0).sort_values())
print(f"Total mars 2020 : {mars['total'].sum():,.0f} EUR")