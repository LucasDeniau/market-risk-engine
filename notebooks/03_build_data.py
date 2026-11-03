"""Construit le jeu de données de marché complet, le contrôle, puis l'enregistre."""

from pathlib import Path

import numpy as np

from riskengine.config import load_config
from riskengine.data.loader import build_market_data, quality_report

# 1. Construction
cfg = load_config("config/portfolio.yaml")
data = build_market_data(cfg)
print(f"{len(data)} jours, du {data.index[0].date()} au {data.index[-1].date()}")

# 2. Contrôle qualité des séries de prix
prix = [e["ticker"] for e in cfg["equities"]] + ["index_level"]
print()
print(quality_report(data[prix]))

# 3. Sauts de plus de 25 % en un jour, à vérifier un par un
log_ret = np.log(data[prix]).diff()
empile = log_ret.stack()
sauts = empile[empile.abs() > 0.25]
print()
print("Sauts à vérifier (log-rendement) :")
print(sauts if not sauts.empty else "aucun")

# 4. Données de marché
print()
print(f"Vol issue du proxy : {(data['vol_source'] == 'proxy_vix').mean():.1%} des jours")
print(f"Taux sans risque : min {data['rate'].min():.4f} | max {data['rate'].max():.4f}")

# 5. Aucune valeur manquante ne doit rester
manquants = data.isna().sum()
manquants = manquants[manquants > 0]
print()
print("Valeurs manquantes :", "aucune" if manquants.empty else "")
if not manquants.empty:
    print(manquants)

# 6. Enregistrement
out_dir = Path(cfg["data"]["processed_dir"])
out_dir.mkdir(parents=True, exist_ok=True)
data.to_parquet(out_dir / "market_data.parquet")
print(f"Enregistré : {out_dir / 'market_data.parquet'}")