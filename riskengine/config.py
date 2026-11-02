"""Chargement et validation de la configuration YAML."""

from pathlib import Path

import yaml


def load_config(path: str | Path) -> dict:
    """Lit le fichier YAML, le valide et renvoie un dictionnaire."""
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    validate_config(cfg)
    return cfg


def validate_config(cfg: dict) -> None:
    """Lève ValueError si la configuration contient une erreur."""
    # 1. Les sections obligatoires sont présentes
    for section in ("data", "market", "equities", "options"):
        if section not in cfg:
            raise ValueError(f"Section manquante dans la configuration : {section}")

    # 2. Pas de ticker en double
    tickers = [e["ticker"] for e in cfg["equities"]]
    doublons = {t for t in tickers if tickers.count(t) > 1}
    if doublons:
        raise ValueError(f"Tickers en double dans la configuration : {doublons}")

    # 3. Chaque action a une devise gérée (EUR ou USD)
    for e in cfg["equities"]:
        if e["currency"] not in ("EUR", "USD"):
            raise ValueError(f"Devise non gérée pour l'action {e['ticker']} : {e['currency']}")

    for p in cfg["options"]["positions"]:
        # 4. Chaque option est un call ou un put
        if p["type"] not in ("call", "put"):
            raise ValueError(f"Type d'option non géré pour l'option {p['id']} : {p['type']}")
         

        # 5. Moneyness et maturité strictement positives
        if p["moneyness"] <= 0:
            raise ValueError(f"Moneyness non valide pour l'option {p['id']} : {p['moneyness']}")
        if p["maturity_months"] <= 0:
            raise ValueError(f"Maturité non valide pour l'option {p['id']} : {p['maturity_months']}")