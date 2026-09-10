from src.services.market_decision_service import (
    get_best_market_from_agmarknet,
)


result = get_best_market_from_agmarknet(
    state="West Bengal",
    district="Nadia",
    commodity="Tomato",
    quantity=50,
    mode="sell",
    transport_costs={},
)


print("\n===== REAL BEST MARKET =====")

for key, value in result.items():
    print(f"{key}: {value}")

print("============================\n")