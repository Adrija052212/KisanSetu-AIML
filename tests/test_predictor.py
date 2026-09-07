import pandas as pd
import pytest

from src.forecasting.predictor import (
    prepare_prediction_features,
    predict_price,
)
from src.schemas import PriceForecast


class DummyModel:
    """Simple fake model for testing predictor logic."""

    def predict(self, X):
        return [2500.0]


def create_sample_history():
    dates = pd.date_range(
        start="2026-08-01",
        end="2026-09-04",
        freq="D",
    )

    rows = []

    for i, date in enumerate(dates):
        rows.append(
            {
                "Date": date,
                "State": "West Bengal",
                "District": "North 24 Parganas",
                "Market": "Barasat",
                "Commodity_Group": "Vegetables",
                "Commodity": "Onion",
                "Variety": "Red Onion",
                "Grade": "A",
                "Min_Price": 2200 + i,
                "Max_Price": 2800 + i,
                "Modal_Price": 2500 + i,
                "Price_Unit": "Rs./Quintal",
                "Arrival_Quantity": 100 + i,
                "Arrival_Unit": "Quintal",
            }
        )

    return pd.DataFrame(rows)


def test_prepare_prediction_features():
    history = create_sample_history()

    X, prediction_row = prepare_prediction_features(
        history
    )

    assert len(X) == 1
    assert X.shape[1] == 23

    assert prediction_row.iloc[0]["Commodity"] == "Onion"

    assert (
        prediction_row.iloc[0]["Date"]
        == pd.Timestamp("2026-09-05")
    )


def test_prediction_returns_price_forecast():
    history = create_sample_history()

    model = DummyModel()

    result = predict_price(
        history,
        model=model,
    )

    assert isinstance(result, PriceForecast)

    assert result.commodity == "Onion"
    assert result.market == "Barasat"

    assert result.forecast_date == pd.Timestamp(
        "2026-09-05"
    ).date()

    assert result.predicted_price == 2500.0

    assert (
        result.model_version
        == "global_xgboost_reduced_v1"
    )


def test_prediction_uses_next_day():
    history = create_sample_history()

    model = DummyModel()

    result = predict_price(
        history,
        model=model,
    )

    latest_date = history["Date"].max().date()

    assert result.forecast_date == (
        latest_date + pd.Timedelta(days=1)
    )


def test_missing_required_column_raises_error():
    history = create_sample_history()

    history = history.drop(
        columns=["Modal_Price"]
    )

    with pytest.raises(ValueError):
        prepare_prediction_features(history)


def test_empty_history_raises_error():
    history = create_sample_history()

    history = history.iloc[0:0]

    with pytest.raises(ValueError):
        prepare_prediction_features(history)