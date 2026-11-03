"""Téléchargement, alignement et contrôle des données de marché."""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from riskengine.data.proxy import fit_linear_proxy


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


def load_vstoxx(path: str | Path) -> pd.Series:
    """Lit l'historique officiel du VSTOXX (fichier STOXX h_vstoxx.txt).

    Renvoie la colonne V2TX (vol implicite ATM 30 jours, en points),
    indexée par date.
    """
    df = pd.read_csv(path, skiprows=2, index_col=0, na_values="NA")
    df.index = pd.to_datetime(df.index, format="%d.%m.%Y")
    return df["V2TX"].sort_index()


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


def _plus_long_plat(s: pd.Series) -> int:
    """Plus grand nombre de jours consécutifs où le prix ne bouge pas."""
    inchange = (s.diff() == 0).to_numpy()
    record = courant = 0
    for flag in inchange:
        courant = courant + 1 if flag else 0
        record = max(record, courant)
    return record


def quality_report(prices: pd.DataFrame, seuil_saut: float = 0.25) -> pd.DataFrame:
    """Contrôle qualité : une ligne par actif, à relire avant toute VaR."""
    rows = {}
    for col in prices.columns:
        s = prices[col]
        log_ret = np.log(s).diff()
        rows[col] = {
            "premiere_date": s.dropna().index[0] if not s.dropna().empty else None,
            "nb_manquants": s.isna().sum(),
            "plus_long_plat": _plus_long_plat(s),
            "nb_sauts": (np.abs(log_ret) > seuil_saut).sum()
        }
    return pd.DataFrame(rows).T


def build_market_data(cfg: dict, refresh: bool = False) -> pd.DataFrame:
    """Construit le jeu de données quotidien du moteur de risque.

    Une ligne par jour de cotation de l'Euro Stoxx 50 ; colonnes :
    prix des actions en EUR, niveau de l'indice, vol ATM, EUR/USD, dividende.
    """
    d, m = cfg["data"], cfg["market"]
    raw_dir = Path(d["raw_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    close_path = raw_dir / "close.parquet"
    adj_path = raw_dir / "adj_close.parquet"

    # 1. Téléchargement Yahoo, ou lecture du cache s'il existe déjà
    if refresh or not close_path.exists():
        tickers = [e["ticker"] for e in cfg["equities"]]
        tickers += [m["index"], m["vol_index_fallback"]]
        close, adj = download_yahoo(tickers, d["start"], d["end"])
        close.to_parquet(close_path)
        adj.to_parquet(adj_path)
    close = pd.read_parquet(close_path)
    adj = pd.read_parquet(adj_path)

    # 2. Calendrier de référence et alignement
    calendar = close[m["index"]].dropna().index
    close = align_to_calendar(close, calendar)
    adj = align_to_calendar(adj, calendar)
    eurusd = align_to_calendar(load_ecb_eurusd(m["fx_file"]), calendar)
    rate = load_fred_rate(m["rate_file"])
    rate = rate.reindex(rate.index.union(calendar)).ffill().reindex(calendar)

    # 3. Actions : prix ajustés, convertis en EUR si besoin
    out = pd.DataFrame(index=calendar)
    for e in cfg["equities"]:
        px = adj[e["ticker"]]
        if e["currency"] == "USD":
            px = to_eur(px, eurusd)
        out[e["ticker"]] = px

    # 4. Données de marché : prix bruts
    out["index_level"] = close[m["index"]]

    # Volatilité implicite ATM : VSTOXX officiel, puis proxy calibré sur le VIX
    vstoxx = load_vstoxx(m["vstoxx_file"]).reindex(calendar)
    vix = close[m["vol_index_fallback"]]
    fit = fit_linear_proxy(vstoxx, vix)
    proxy = fit["a"] + fit["b"] * vix
    out["atm_vol"] = vstoxx.fillna(proxy) / 100
    out["vol_source"] = np.where(vstoxx.notna(), "vstoxx", "proxy_vix")

    out["eurusd"] = eurusd
    out["rate"] = rate
    out["div_yield"] = m["dividend_yield"]
    out.index.name = "date"
    return out


def load_ecb_eurusd(path: str | Path) -> pd.Series:
    """Lit le taux de référence BCE EUR/USD (dollars pour 1 euro).

    Fichier CSV de l'API BCE (série EXR.D.USD.EUR.SP00.A), taux fixé à 14h15 CET.
    """
    df = pd.read_csv(path, usecols=["TIME_PERIOD", "OBS_VALUE"], index_col="TIME_PERIOD")
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
    df.index.name = "date"
    return df["OBS_VALUE"].rename("eurusd").sort_index()


def load_fred_rate(path: str | Path) -> pd.Series:
    """Lit un taux mensuel FRED (en %) et le renvoie en décimal.

    Chaque valeur est la moyenne du mois : elle est décalée d'un mois
    pour n'être utilisée qu'une fois connue (pas de biais d'anticipation).
    """
    df = pd.read_csv(path, index_col="observation_date")
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
    s = df.iloc[:, 0] / 100                       # première colonne, en décimal

    s.index = s.index + pd.DateOffset(months=1)   # décalage d'un mois
    s.index.name = "date"
    return s.rename("rate").sort_index()