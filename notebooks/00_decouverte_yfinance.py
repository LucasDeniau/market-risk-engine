"""Exploration : à quoi ressemblent les données Yahoo Finance ?"""

import yfinance as yf

data = yf.download(
    ["TTE.PA", "^STOXX50E"],
    start="2024-01-01",
    end="2024-12-31",
    auto_adjust=False,  # garder Close ET Adj Close séparés
    progress=False,
)

print("Colonnes :")
print(data.columns.tolist()[:6])
print()
print(data.tail(3))
print()

# Rapport entre prix ajusté et prix brut pour TotalEnergies
tte = data.xs("TTE.PA", axis=1, level=1)[["Close", "Adj Close"]].copy()
tte["ratio"] = tte["Adj Close"] / tte["Close"]
print("Valeurs distinctes du ratio Adj Close / Close pour TTE.PA :")
print(tte["ratio"].round(4).drop_duplicates())
print()

# Même chose pour l'indice
idx = data.xs("^STOXX50E", axis=1, level=1)[["Close", "Adj Close"]]
print("Prix ajusté de l'indice identique au prix brut ?",
    (idx["Close"] - idx["Adj Close"]).abs().max() < 1e-9)