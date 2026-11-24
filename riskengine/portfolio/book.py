"""Book d'options roulé mensuellement, à moneyness et maturité constantes."""

import numpy as np
import pandas as pd


def roll_dates(calendar: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Premier jour de cotation de chaque mois : les dates de renouvellement."""
    jours = pd.Series(calendar, index=calendar)
    premiers = jours.groupby(calendar.to_period("M")).first()
    return pd.DatetimeIndex(premiers.to_numpy())


def option_positions(cfg: dict, data: pd.DataFrame) -> pd.DataFrame:
    """Caractéristiques de chaque option détenue, jour par jour.

    Une ligne par (date, option) : strike, échéance et nombre de contrats,
    fixés à la date de roll et inchangés jusqu'au roll suivant.
    """
    calendar = data.index
    rolls = roll_dates(calendar)

    # Pour chaque jour, la date du dernier roll (celui qui a ouvert les positions)
    periode = np.searchsorted(rolls, calendar, side="right") - 1
    roll_du_jour = rolls[periode]
    spot_au_roll = data["index_level"].reindex(roll_du_jour).to_numpy()
    multiplicateur = cfg["options"]["multiplier"]

    tables = []
    for p in cfg["options"]["positions"]:
        tables.append(pd.DataFrame({
            "date": calendar,
            "id": p["id"],
            "type": p["type"],
            "roll_date": roll_du_jour,
            "strike": p["moneyness"] * spot_au_roll,
            "expiry": roll_du_jour + pd.DateOffset(months=p["maturity_months"]),
            "contracts": p["notional_eur"] / (multiplicateur * spot_au_roll),
        }))
    return pd.concat(tables, ignore_index=True)