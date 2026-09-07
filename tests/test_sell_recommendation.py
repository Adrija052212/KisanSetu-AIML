from src.recommendations.sell_recommendation import (
    get_sell_recommendation
)


def test_wait_recommendation():
    result = get_sell_recommendation(
        current_price=2500,
        predicted_price=2700,
        transport_cost=100,
        quantity=10
    )

    assert result["recommendation"] == "WAIT"
    assert result["current_net_price"] == 2400
    assert result["expected_net_price"] == 2600
    assert result["expected_change"] == 200


def test_sell_recommendation():
    result = get_sell_recommendation(
        current_price=2700,
        predicted_price=2680,
        transport_cost=100,
        quantity=10
    )

    assert result["recommendation"] == "SELL"
    assert result["current_net_price"] == 2600
    assert result["expected_net_price"] == 2580


def test_transport_cost():
    result = get_sell_recommendation(
        current_price=2500,
        predicted_price=2600,
        transport_cost=150,
        quantity=5
    )

    assert result["current_net_price"] == 2350
    assert result["expected_net_price"] == 2450


def test_minimum_change_threshold():
    result = get_sell_recommendation(
        current_price=2500,
        predicted_price=2525,
        transport_cost=0,
        quantity=1,
        min_change_percent=2.0
    )

    assert result["recommendation"] == "SELL"


def test_invalid_quantity():
    try:
        get_sell_recommendation(
            current_price=2500,
            predicted_price=2600,
            quantity=0
        )
        assert False
    except ValueError:
        assert True