"""Construit le jeu de données complet et affiche le contrôle qualité."""

from riskengine.config import load_config
from riskengine.data.loader import build_market_data, quality_report

cfg = load_config("config/portfolio.yaml")
data = build_market_data(cfg)

prix = [e["ticker"] for e in cfg["equities"]] + ["index_level"]
print(quality_report(data[prix]))
print()
print(f"{len(data)} jours, du {data.index[0].date()} au {data.index[-1].date()}")
print(f"Vol issue du VIX (repli) : {data['vol_from_fallback'].mean():.1%} des jours")