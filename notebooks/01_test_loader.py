"""Test manuel du loader sur une petite période."""

from riskengine.data.loader import align_to_calendar, download_yahoo

close, adj = download_yahoo(["TTE.PA", "SPY", "^STOXX50E"], "2024-06-25", "2024-07-10")
calendar = close["^STOXX50E"].dropna().index

print("Avant alignement :")
print(close)
print()
print("Après alignement :")
print(align_to_calendar(close, calendar))

from riskengine.data.loader import to_eur

aligned = align_to_calendar(close, calendar)
fx, _ = download_yahoo(["EURUSD=X"], "2024-06-25", "2024-07-10")
fx_aligned = align_to_calendar(fx, calendar)

spy_eur = to_eur(aligned["SPY"], fx_aligned["EURUSD=X"])
print()
print("SPY en euros :")
print(spy_eur.round(2))