"""Test du contrôle qualité sur des données fabriquées."""

import numpy as np
import pandas as pd

from riskengine.data.loader import quality_report

dates = pd.bdate_range("2024-01-01", periods=10)
prix = pd.DataFrame({
    "normal": [100, 101, 99, 102, 103, 101, 104, 105, 103, 106],
    "fige":   [50, 50, 50, 50, 50, 50, 51, 52, 51, 53],
    "split":  [200, 202, 204, 102, 103, 101, 104, 105, 103, 106],
    "trou":   [10, 11, np.nan, np.nan, np.nan, np.nan, 12, 13, 12, 14],
}, index=dates, dtype=float)

print(quality_report(prix))