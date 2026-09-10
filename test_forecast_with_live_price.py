from src.mcp.tools.prices import forecast_price_tool


result = forecast_price_tool(
    state="West Bengal",
    district="Nadia",
    market="Ranaghat APMC",
    commodity="Tomato",
    variety="Other",
    grade="FAQ",
)

print("\n===== FORECAST WITH LIVE PRICE =====")

for key, value in result.items():
    print(f"{key}: {value}")

print("====================================\n")