import pytest

from src.recommendations.timing import recommend_best_time


def test_sell_best_time():
    predictions = [
        {"date": "2026-09-06", "predicted_price": 2400},
        {"date": "2026-09-07", "predicted_price": 2460},
        {"date": "2026-09-08", "predicted_price": 2510},
    ]

    result = recommend_best_time(
        predictions,
        mode="sell"
    )

    assert result["recommendation"] == "SELL"
    assert result["best_date"] == "2026-09-08"
    assert result["best_predicted_price"] == 2510

    assert result["ranked_predictions"][0]["rank"] == 1
    assert result["ranked_predictions"][0]["date"] == "2026-09-08"


def test_buy_best_time():
    predictions = [
        {"date": "2026-09-06", "predicted_price": 2400},
        {"date": "2026-09-07", "predicted_price": 2460},
        {"date": "2026-09-08", "predicted_price": 2510},
    ]

    result = recommend_best_time(
        predictions,
        mode="buy"
    )

    assert result["recommendation"] == "BUY"
    assert result["best_date"] == "2026-09-06"
    assert result["best_predicted_price"] == 2400


def test_empty_predictions():
    with pytest.raises(ValueError):
        recommend_best_time([])


def test_invalid_mode():
    predictions = [
        {"date": "2026-09-06", "predicted_price": 2400}
    ]

    with pytest.raises(ValueError):
        recommend_best_time(
            predictions,
            mode="hold"
        )


def test_negative_predicted_price():
    predictions = [
        {"date": "2026-09-06", "predicted_price": -100}
    ]

    with pytest.raises(ValueError):
        recommend_best_time(predictions)