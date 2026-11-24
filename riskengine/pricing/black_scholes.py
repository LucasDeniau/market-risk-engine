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
    
    
def greeks(S, K, T, r, sigma, q=0.0, option="call"):
    """Grecques BSM, en dérivées brutes.

    vega : par unité de sigma en décimal (vega / 100 = effet de +1 point de vol)
    theta : par année, = -dV/dT (theta / 365 = effet d'un jour)
    """
    cp = 1.0 if option == "call" else -1.0
    d1, d2 = d1_d2(S, K, T, r, sigma, q)
    racine_t = np.sqrt(T)
    act_q = np.exp(-q * T)
    act_r = np.exp(-r * T)
    densite = norm.pdf(d1)

    delta = cp * act_q * norm.cdf(cp * d1)
    gamma = act_q * densite / (S * sigma * racine_t)
    vega = S * act_q * densite * racine_t
    theta = (-S * act_q * densite * sigma / (2 * racine_t)
             - cp * r * K * act_r * norm.cdf(cp * d2)
             + cp * q * S * act_q * norm.cdf(cp * d1))
    rho = cp * K * T * act_r * norm.cdf(cp * d2)
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}