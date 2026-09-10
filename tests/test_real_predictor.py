import pandas as pd

from src.forecasting.predictor import (
    load_price_model,
    predict_price,
)
from src.schemas import PriceForecast


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


def test_real_model_can_be_loaded():
    model = load_price_model()

    assert model is not None


def test_real_model_can_predict():
    history = create_sample_history()

    result = predict_price(history)

    assert isinstance(result, PriceForecast)

    assert result.commodity == "Onion"
    assert result.market == "Barasat"

    assert result.forecast_date == pd.Timestamp(
        "2026-09-05"
    ).date()

    assert result.predicted_price >= 0

    assert (
        result.model_version
        == "global_xgboost_reduced_v1"
    )