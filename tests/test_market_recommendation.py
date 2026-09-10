import pytest

from src.recommendations.market_recommendation import (
    recommend_best_market,
)


# ============================================================
# Test SELL recommendation
# ============================================================

def test_sell_recommends_market_with_highest_net_price():

    markets = [
        {
            "market": "Market A",
            "current_price": 2500,
            "transport_cost": 100,
        },
        {
            "market": "Market B",
            "current_price": 2650,
            "transport_cost": 80,
        },
        {
            "market": "Market C",
            "current_price": 2700,
            "transport_cost": 250,
        },
    ]

    result = recommend_best_market(
        markets=markets,
        quantity=10,
        mode="sell",
    )

    assert result["best_market"] == "Market B"

    assert (
        result["markets"][0]["current_effective_price"]
        == 2570
    )

    assert result["markets"][0]["rank"] == 1


# ============================================================
# Test BUY recommendation
# ============================================================

def test_buy_recommends_market_with_lowest_effective_cost():

    markets = [
        {
            "market": "Market A",
            "current_price": 2500,
            "transport_cost": 100,
        },
        {
            "market": "Market B",
            "current_price": 2400,
            "transport_cost": 80,
        },
        {
            "market": "Market C",
            "current_price": 2300,
            "transport_cost": 250,
        },
    ]

    result = recommend_best_market(
        markets=markets,
        quantity=10,
        mode="buy",
    )

    # A = 2500 + 100 = 2600
    # B = 2400 + 80  = 2480
    # C = 2300 + 250 = 2550
    #
    # Therefore B is the cheapest effective option.

    assert result["best_market"] == "Market B"

    assert (
        result["markets"][0]["current_effective_price"]
        == 2480
    )

    assert result["markets"][0]["rank"] == 1


# ============================================================
# Test quantity calculation
# ============================================================

def test_market_total_calculation():

    markets = [
        {
            "market": "Market A",
            "current_price": 2500,
            "transport_cost": 100,
        },
        {
            "market": "Market B",
            "current_price": 2650,
            "transport_cost": 80,
        },
    ]

    result = recommend_best_market(
        markets=markets,
        quantity=10,
        mode="sell",
    )

    # Market B:
    # 2650 - 80 = 2570 per quintal
    # 2570 * 10 = 25700

    assert (
        result["markets"][0]["current_total"]
        == 25700
    )


# ============================================================
# Test predicted price
# ============================================================

def test_predicted_price_calculation():

    markets = [
        {
            "market": "Market A",
            "current_price": 2500,
            "transport_cost": 100,
            "predicted_price": 2600,
        },
        {
            "market": "Market B",
            "current_price": 2400,
            "transport_cost": 80,
            "predicted_price": 2500,
        },
    ]

    result = recommend_best_market(
        markets=markets,
        quantity=10,
        mode="sell",
    )

    best_market = result["markets"][0]

    assert best_market["predicted_price"] == 2600

    assert (
        best_market["predicted_effective_price"]
        == 2500
    )

    assert (
        best_market["predicted_total"]
        == 25000
    )

    assert (
        best_market["expected_change"]
        == 100
    )


# ============================================================
# Test invalid mode
# ============================================================

def test_invalid_mode():

    markets = [
        {
            "market": "Market A",
            "current_price": 2500,
            "transport_cost": 100,
        }
    ]

    with pytest.raises(ValueError):

        recommend_best_market(
            markets=markets,
            quantity=10,
            mode="invalid",
        )