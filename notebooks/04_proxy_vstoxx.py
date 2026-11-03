"""Calibration et validation du proxy VSTOXX ≈ a + b·VIX."""

import numpy as np
import pandas as pd

from riskengine.data.loader import load_vstoxx
from riskengine.data.proxy import fit_linear_proxy

vstoxx = load_vstoxx("data/raw/h_vstoxx.txt")
vix = pd.read_parquet("data/raw/close.parquet")["^VIX"]

# 1. Calibration sur 2007-2013
fit = fit_linear_proxy(vstoxx.loc["2007":"2013"], vix.loc["2007":"2013"])
print(f"a = {fit['a']:.2f}, b = {fit['b']:.3f}, R² = {fit['r2']:.3f}, "
      f"RMSE = {fit['rmse']:.2f} points ({fit['n']} jours)")

# 2. Validation hors échantillon sur 2014-2016
test = pd.concat([vstoxx.loc["2014":], vix.loc["2014":"2016-02-12"]], axis=1, sort=True).dropna()
pred = fit["a"] + fit["b"] * test.iloc[:, 1]
erreur = test.iloc[:, 0] - pred
print(f"RMSE hors échantillon (2014-2016) : {np.sqrt((erreur ** 2).mean()):.2f} points")

# 3. Le proxy face à des pics connus, après la fin du fichier
for date, vrai in [("2020-03-16", 85.62), ("2024-08-05", 31.17), ("2025-04-07", 46.72)]:
    proxy = fit["a"] + fit["b"] * vix.loc[date]
    print(f"{date} : VIX = {vix.loc[date]:.1f}, proxy = {proxy:.1f}, vrai VSTOXX = {vrai}")