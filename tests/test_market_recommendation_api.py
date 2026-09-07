import requests


API_URL = "http://127.0.0.1:8000/recommend/market"


# ============================================================
# Test SELL market recommendation
# ============================================================

sell_payload = {
    "markets": [
        {
            "market": "Market A",
            "current_price": 2500,
            "transport_cost": 100
        },
        {
            "market": "Market B",
            "current_price": 2650,
            "transport_cost": 80
        },
        {
            "market": "Market C",
            "current_price": 2700,
            "transport_cost": 250
        }
    ],
    "quantity": 10,
    "mode": "sell"
}


print("=" * 60)
print("TEST 1: SELL MARKET RECOMMENDATION")
print("=" * 60)

response = requests.post(
    API_URL,
    json=sell_payload
)

print("\nAPI status:", response.status_code)
print("\nAPI response:")

try:
    print(response.json())
except Exception:
    print(response.text)


# ============================================================
# Test BUY market recommendation
# ============================================================

buy_payload = {
    "markets": [
        {
            "market": "Market A",
            "current_price": 2500,
            "transport_cost": 100
        },
        {
            "market": "Market B",
            "current_price": 2400,
            "transport_cost": 80
        },
        {
            "market": "Market C",
            "current_price": 2300,
            "transport_cost": 250
        }
    ],
    "quantity": 10,
    "mode": "buy"
}


print("\n")
print("=" * 60)
print("TEST 2: BUY MARKET RECOMMENDATION")
print("=" * 60)

response = requests.post(
    API_URL,
    json=buy_payload
)

print("\nAPI status:", response.status_code)
print("\nAPI response:")

try:
    print(response.json())
except Exception:
    print(response.text)