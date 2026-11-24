"""Pricer Black-Scholes-Merton pour options européennes avec dividende continu q.

Conventions : T en années, r et q en taux continus, sigma en décimal.
Tous les arguments acceptent des scalaires ou des tableaux NumPy.
"""

import numpy as np
from scipy.stats import norm


def d1_d2(S, K, T, r, sigma, q=0.0):
    """Renvoie (d1, d2) de Black-Scholes-Merton."""
    vol_racine_t = sigma * np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / vol_racine_t
    d2 = d1 - vol_racine_t
    return d1, d2


def price(S, K, T, r, sigma, q=0.0, option="call"):
    """Prix BSM d'un call ou d'un put européen."""
    cp = 1.0 if option == "call" else -1.0
    d1, d2 = d1_d2(S, K, T, r, sigma, q)
    return cp * (S * np.exp(-q * T) * norm.cdf(cp * d1)
                 - K * np.exp(-r * T) * norm.cdf(cp * d2))