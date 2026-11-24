"""Valorisation quotidienne du book et P&L jour par jour."""

import numpy as np
import pandas as pd

from riskengine.pricing.black_scholes import price

MARCHE = ["index_level", "atm_vol", "rate", "div_yield"]


def option_values(pos: pd.DataFrame, data: pd.DataFrame, multiplier: float,
                  horizon: int = 0) -> pd.DataFrame:
    """Valeur en EUR des options détenues à t, valorisées avec le marché de t + horizon.

    horizon=0 : valeur du book au jour t.
    horizon=1 : valeur du même book (positions figées) au jour de cotation suivant.
    Renvoie un tableau : une ligne par date t, une colonne par option.
    """
    dates = pd.Series(data.index, index=data.index).shift(-horizon)
    marche = data[MARCHE].shift(-horizon)

    m = marche.reindex(pos["date"]).to_numpy()
    date_valo = dates.reindex(pos["date"]).to_numpy()
    T = (pos["expiry"].to_numpy() - date_valo) / np.timedelta64(365, "D")

    prix = price(S=m[:, 0], K=pos["strike"].to_numpy(), T=T, r=m[:, 2],
                 sigma=m[:, 1], q=m[:, 3], option=pos["type"].to_numpy())
    valeur = prix * pos["contracts"].to_numpy() * multiplier

    table = pd.DataFrame({"date": pos["date"], "id": pos["id"], "valeur": valeur})
    return table.pivot(index="date", columns="id", values="valeur")


def daily_pnl(cfg: dict, data: pd.DataFrame, pos: pd.DataFrame) -> pd.DataFrame:
    """P&L de t à t+1 du portefeuille détenu à t, par ligne et au total (en EUR)."""
    multiplicateur = cfg["options"]["multiplier"]
    pnl_options = (option_values(pos, data, multiplicateur, horizon=1)
                   - option_values(pos, data, multiplicateur, horizon=0))

    tickers = [e["ticker"] for e in cfg["equities"]]
    notionnels = pd.Series({e["ticker"]: e["notional_eur"] for e in cfg["equities"]})
    rendements = data[tickers].shift(-1) / data[tickers] - 1
    pnl_actions = rendements * notionnels

    pnl = pd.concat([pnl_actions, pnl_options], axis=1)
    pnl["total"] = pnl.sum(axis=1)
    return pnl.iloc[:-1]  # le dernier jour n'a pas de lendemain