"""Vérifie le book roulé autour d'une date de roll (mars 2020)."""

import pandas as pd

from riskengine.config import load_config
from riskengine.portfolio.book import option_positions

cfg = load_config("config/portfolio.yaml")
data = pd.read_parquet("data/processed/market_data.parquet")
pos = option_positions(cfg, data)

put = pos[pos["id"] == "short_put_3m_90"].set_index("date")
print(put.loc["2020-02-26":"2020-03-04", ["roll_date", "strike", "expiry", "contracts"]].round(2))
print()
print("Indice au 3 février 2020 :", round(data.loc["2020-02-03", "index_level"], 2))
print("Indice au 2 mars 2020 :", round(data.loc["2020-03-02", "index_level"], 2))