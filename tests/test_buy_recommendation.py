from src.recommendations.buy_recommendation import (
    get_buy_recommendation
)


def test_buy_recommendation():
    result = get_buy_recommendation(
        current_price=2500,
        predicted_price=2800,
        quantity=10
    )

    assert result["recommendation"] == "BUY"
    assert result["expected_change"] == 300
    assert result["expected_change_percent"] == 12.0
    assert result["expected_gain"] == 3000


def test_wait_recommendation():
    result = get_buy_recommendation(
        current_price=2500,
        predicted_price=2510,
        quantity=10
    )

    assert result["recommendation"] == "WAIT"


def test_price_decrease():
    result = get_buy_recommendation(
        current_price=2500,
        predicted_price=2400,
        quantity=10
    )

    assert result["recommendation"] == "WAIT"
    assert result["expected_change"] == -100
    assert result["expected_gain"] == -1000


def test_threshold():
    result = get_buy_recommendation(
        current_price=2500,
        predicted_price=2550,
        quantity=10,
        min_change_percent=2.0
    )

    assert result["recommendation"] == "BUY"


def test_invalid_quantity():
    try:
        get_buy_recommendation(
            current_price=2500,
            predicted_price=2800,
            quantity=0
        )
        assert False
    except ValueError:
        assert True