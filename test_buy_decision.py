from src.services.decision_service import (
    get_buy_decision_from_market,
)


result = get_buy_decision_from_market(
    state="West Bengal",
    district="Nadia",
    market="Ranaghat APMC",
    commodity="Tomato",
    variety="Other",
    grade="FAQ",
    quantity=50,
    min_change_percent=2.0,
)

print("\n===== REAL BUY DECISION =====")

for key, value in result.items():
    print(f"{key}: {value}")

print("=============================\n")