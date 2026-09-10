from src.data_access.agmarknet_data import (
    get_current_market_price_by_name,
)


result = get_current_market_price_by_name(
    date="2026-09-08",
    state="West Bengal",
    district="Nadia",
    market="Ranaghat APMC",
    commodity="Tomato",
    variety="Other",
    grade="FAQ",
)

print("\n===== CURRENT PRICE BY NAME =====")

for key, value in result.items():
    print(f"{key}: {value}")

print("=================================\n")