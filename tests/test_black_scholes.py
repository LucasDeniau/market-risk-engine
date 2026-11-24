"""Tests du pricer Black-Scholes-Merton."""

import numpy as np
import pytest

from riskengine.pricing.black_scholes import greeks, price

# Cas variés : à la monnaie, en dehors, avec dividende, maturité longue, taux négatif
CASES = [
    {"S": 100.0, "K": 100.0, "T": 1.0, "r": 0.03, "sigma": 0.20, "q": 0.02},
    {"S": 100.0, "K": 80.0, "T": 0.25, "r": 0.01, "sigma": 0.35, "q": 0.00},
    {"S": 5000.0, "K": 4500.0, "T": 0.5, "r": 0.035, "sigma": 0.18, "q": 0.03},
    {"S": 50.0, "K": 60.0, "T": 2.0, "r": -0.005, "sigma": 0.50, "q": 0.01},
]


# 1. Valeurs de référence
def test_valeurs_hull():
    assert price(42, 40, 0.5, 0.10, 0.20, option="call") == pytest.approx(4.76, abs=5e-3)
    assert price(42, 40, 0.5, 0.10, 0.20, option="put") == pytest.approx(0.81, abs=5e-3)


# 2. Non-arbitrage
@pytest.mark.parametrize("c", CASES)
def test_parite_call_put(c):
    call = price(**c, option="call")
    put = price(**c, option="put")
    forward_actualise = c["S"] * np.exp(-c["q"] * c["T"]) - c["K"] * np.exp(-c["r"] * c["T"])
    assert call - put == pytest.approx(forward_actualise, abs=1e-10)


@pytest.mark.parametrize("c", CASES)
def test_bornes_du_call(c):
    call = price(**c, option="call")
    borne_basse = max(c["S"] * np.exp(-c["q"] * c["T"]) - c["K"] * np.exp(-c["r"] * c["T"]), 0)
    borne_haute = c["S"] * np.exp(-c["q"] * c["T"])
    assert borne_basse <= call <= borne_haute


# 3. Grecques contre différences finies
@pytest.mark.parametrize("c", CASES)
@pytest.mark.parametrize("option", ["call", "put"])
def test_grecques_par_differences_finies(c, option):
    g = greeks(**c, option=option)

    def p(**changement):
        return price(**(c | changement), option=option)

    S, T, r, sigma = c["S"], c["T"], c["r"], c["sigma"]
    hS, h = 1e-4 * S, 1e-6
    numerique = {
        "delta": (p(S=S + hS) - p(S=S - hS)) / (2 * hS),
        "gamma": (p(S=S + hS) - 2 * p() + p(S=S - hS)) / hS**2,
        "vega": (p(sigma=sigma + h) - p(sigma=sigma - h)) / (2 * h),
        "theta": -(p(T=T + h) - p(T=T - h)) / (2 * h),
        "rho": (p(r=r + h) - p(r=r - h)) / (2 * h),
    }
    for nom, valeur in numerique.items():
        assert g[nom] == pytest.approx(valeur, rel=1e-4, abs=1e-6), nom


@pytest.mark.parametrize("c", CASES)
def test_relations_entre_call_et_put(c):
    gc = greeks(**c, option="call")
    gp = greeks(**c, option="put")
    assert gc["delta"] - gp["delta"] == pytest.approx(np.exp(-c["q"] * c["T"]))
    assert gc["gamma"] == pytest.approx(gp["gamma"])
    assert gc["vega"] == pytest.approx(gp["vega"])


# 4. Vectorisation : un tableau de prix d'un coup
def test_vectorisation():
    S = np.array([4500.0, 5000.0, 5500.0])
    prix = price(S, 5000.0, 0.25, 0.03, 0.2, 0.03)
    assert prix.shape == (3,)
    assert np.all(np.diff(prix) > 0)  # un call vaut plus quand l'indice monte
  
    
# 5. Options échues et types mélangés
def test_echeance_valeur_intrinseque():
    assert price(110, 100, 0.0, 0.02, 0.2, option="call") == pytest.approx(10.0)
    assert price(90, 100, 0.0, 0.02, 0.2, option="put") == pytest.approx(10.0)
    assert price(90, 100, -0.01, 0.02, 0.2, option="call") == 0.0


def test_calls_et_puts_melanges():
    prix = price(100.0, 100.0, 1.0, 0.02, 0.2, option=np.array(["call", "put"]))
    assert prix[0] == pytest.approx(price(100, 100, 1.0, 0.02, 0.2, option="call"))
    assert prix[1] == pytest.approx(price(100, 100, 1.0, 0.02, 0.2, option="put"))