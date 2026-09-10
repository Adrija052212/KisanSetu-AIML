from src.services.decision_service import (
    get_sell_decision_from_market,
)


result = get_sell_decision_from_market(
    state="West Bengal",
    district="Nadia",
    market="Ranaghat APMC",
    commodity="Tomato",
    variety="Other",
    grade="FAQ",
    quantity=50,
    transport_cost=0,
    min_change_percent=0,
)


print("\n===== REAL SELL DECISION =====")

for key, value in result.items():
    print(f"{key}: {value}")

print("==============================\n")