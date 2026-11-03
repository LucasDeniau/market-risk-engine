"""Construit le jeu de données complet et affiche le contrôle qualité."""

import numpy as np

from riskengine.config import load_config
from riskengine.data.loader import build_market_data, quality_report

cfg = load_config("config/portfolio.yaml")
data = build_market_data(cfg)

prix = [e["ticker"] for e in cfg["equities"]] + ["index_level"]
print(quality_report(data[prix]))
print()
print(f"{len(data)} jours, du {data.index[0].date()} au {data.index[-1].date()}")
print(f"Vol issue du proxy : {(data['vol_source'] == 'proxy_vix').mean():.1%} des jours")


print()
print("Dates où le SPY en euros manque :")
print(data.index[data["SPY"].isna()].tolist())
print("Le change manque-t-il ces jours-là ?")
print(data.loc[data["SPY"].isna(), "eurusd"])

print()
r = np.log(data["AIR.PA"]).diff()
print("Saut(s) d'Airbus :")
print(r[r.abs() > 0.25])