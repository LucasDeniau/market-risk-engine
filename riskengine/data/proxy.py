"""Reconstruction d'un facteur de risque par un proxy linéaire."""

import numpy as np
import pandas as pd


def fit_linear_proxy(y: pd.Series, x: pd.Series) -> dict:
    """Ajuste y ≈ a + b·x par moindres carrés, sur les dates communes."""
    commun = pd.concat([y, x], axis=1, sort=True).dropna()
    yy, xx = commun.iloc[:, 0], commun.iloc[:, 1]

    b, a = np.polyfit(xx, yy, 1)       
    residus = yy - (a + b * xx) 
    r2 = 1 - (residus.var() / yy.var())         
    rmse = np.sqrt((residus ** 2).mean())   

    return {"a": a, "b": b, "r2": r2, "rmse": rmse, "n": len(commun)}