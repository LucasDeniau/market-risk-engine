"""Test manuel du loader sur une petite période."""

from riskengine.data.loader import align_to_calendar, download_yahoo

close, adj = download_yahoo(["TTE.PA", "SPY", "^STOXX50E"], "2024-06-25", "2024-07-10")
calendar = close["^STOXX50E"].dropna().index

print("Avant alignement :")
print(close)
print()
print("Après alignement :")
print(align_to_calendar(close, calendar))