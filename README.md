# Moteur de risque de marché
![Tests](https://github.com/LucasDeniau/market-risk-engine/actions/workflows/ci.yml/badge.svg)

Mini moteur de risque de marché en Python, construit comme celui d'une équipe risques de marché en banque :
portefeuille multi-actifs en euros avec options sur indice, VaR et Expected Shortfall par plusieurs méthodes,
stress tests et backtesting réglementaire.

> 🚧 Projet en cours de développement. V1 prévue début décembre 2026.

## Portefeuille

- **Actions** : 10 valeurs de la zone euro dans 10 secteurs et 4 pays (Airbus, Mercedes-Benz, BNP Paribas,
  Allianz, TotalEnergies, ASML, LVMH, Sanofi, Air Liquide, Iberdrola) et un ETF S&P 500 converti en euros.
- **Options européennes sur Euro Stoxx 50** : book vendeur de volatilité à court terme (straddle 1 mois,
  put 3 mois 90 %), protégé à plus long terme (put 6 mois 95 %, call 1 an 105 %). Book roulé mensuellement
  à moneyness et maturité constantes.

## Données de marché (2007-2026)

| Donnée | Source | Traitement |
|---|---|---|
| Actions | Yahoo Finance | Prix ajustés des dividendes |
| Euro Stoxx 50 | Yahoo Finance | Indice prix, calendrier de référence |
| Volatilité implicite ATM | VSTOXX officiel (STOXX) jusqu'en 2016, puis proxy | Proxy VSTOXX ≈ 6,05 + 0,90 × VIX, R² = 0,91, erreur hors échantillon de 3 points de vol |
| EUR/USD | Taux de référence BCE | Remplace Yahoo, incomplet en août 2008 |
| Taux sans risque | Taux interbancaire 3 mois zone euro (OCDE via FRED) | Décalé d'un mois pour éviter tout biais d'anticipation |

Contrôle qualité automatique de chaque série : historique, valeurs manquantes, prix figés, sauts extrêmes.

## Avancement

- [x] Structure du package, configuration YAML validée
- [x] Données de marché : téléchargement, alignement, contrôle qualité, proxy de volatilité
- [x] Pricer Black-Scholes-Merton et tests
- [ ] Sensibilités, full revaluation contre delta-gamma-vega
- [ ] VaR et ES : paramétrique, historique, historique filtrée (GARCH), Monte Carlo
- [ ] Backtesting : Kupiec, Christoffersen, feux tricolores de Bâle
- [ ] Stress tests historiques (2008, 2018, 2020, 2022)

## Installation

```bash
pip install -e ".[dev]"
python notebooks/03_build_data.py
```

Les fichiers de données (VSTOXX, BCE, FRED) sont à placer dans `data/raw/` ; ils ne sont pas versionnés.