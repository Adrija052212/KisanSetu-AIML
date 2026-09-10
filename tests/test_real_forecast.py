from src.data_access.market_data import get_market_price_history
from src.data_access.forecast_data import forecast_from_market_records


# ============================================================
# REAL END-TO-END FORECAST TEST
# Supabase → Market History → Forecasting → Trained Model
# ============================================================

STATE = "Andaman and Nicobar"
DISTRICT = "North and Middle Andaman"
MARKET = "Diglipur Vegetable Market (Subhashgram)"
COMMODITY = "Tomato"
VARIETY = "Other"
GRADE = "FAQ"


print("=" * 70)
print("KISANSETU REAL END-TO-END FORECAST TEST")
print("=" * 70)

print("\n1. Fetching real market history from Supabase...")

records = get_market_price_history(
    state=STATE,
    district=DISTRICT,
    market=MARKET,
    commodity=COMMODITY,
    variety=VARIETY,
    grade=GRADE,
    limit=1000,
)

print(f"Records fetched: {len(records)}")

if not records:
    raise RuntimeError("No market history found for this series.")


print("\n2. Checking latest historical record...")

latest = records[-1]

print(f"Latest date:       {latest['Date']}")
print(f"Latest modal price: ₹{latest['Modal_Price']}")
print(f"Latest arrival:    {latest['Arrival_Quantity']}")


print("\n3. Running forecasting pipeline...")

forecast = forecast_from_market_records(records)


print("\n4. FORECAST RESULT")
print("-" * 70)

for key, value in forecast.items():
    print(f"{key}: {value}")


print("\n" + "=" * 70)
print("END-TO-END FORECAST TEST COMPLETED SUCCESSFULLY")
print("=" * 70)