"""Téléchargement, alignement et contrôle des données de marché."""

import warnings

import pandas as pd


def download_yahoo(tickers: list[str], start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Télécharge les prix Yahoo Finance.

    Renvoie (close, adj_close), deux tableaux avec une colonne par ticker :
    - close : prix brut, pour l'indice, la vol et le change ;
    - adj_close : prix ajusté des dividendes, pour les rendements actions.
    """
    import yfinance as yf

    with warnings.catch_warnings():
        # avertissements internes à yfinance, sans effet sur les données
        warnings.filterwarnings("ignore", message=".*inplace keyword.*")
        raw = yf.download(tickers, start=start, end=end, auto_adjust=False, progress=False)

    if raw.empty:
        raise RuntimeError("Yahoo n'a renvoyé aucune donnée")
    return raw["Close"], raw["Adj Close"]


def align_to_calendar(df: pd.DataFrame, calendar: pd.DatetimeIndex,
                      max_ffill: int = 3) -> pd.DataFrame:
    """Aligne df sur le calendrier de référence.

    - les jours hors calendrier sont supprimés ;
    - un trou d'au plus max_ffill jours est comblé par le dernier prix connu ;
    - au-delà, le NaN reste visible.
    """
    df = df.reindex(calendar)
    df = df.ffill(limit=max_ffill)
    return df


def to_eur(price_usd: pd.Series, eurusd: pd.Series) -> pd.Series:
    """Convertit un prix en dollars en euros.

    eurusd cote le nombre de dollars pour 1 euro (ticker EURUSD=X).
    """
    eurusd_aligne = eurusd.reindex(price_usd.index)
    return price_usd / eurusd_aligne