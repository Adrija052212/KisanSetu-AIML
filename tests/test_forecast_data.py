import pandas as pd
import pytest

from unittest.mock import patch
from src.data_access.forecast_data import (
    market_records_to_dataframe,
    forecast_from_market_records,
)


def test_market_records_to_dataframe():
    records = [
        {
            "State": "West Bengal",
            "District": "Nadia",
            "Market": "Krishnanagar",
            "Commodity": "Tomato",
            "Variety": "Local",
            "Grade": "A",
            "Date": "04/09/2026",
            "Modal_Price": "2000",
            "Arrival_Quantity": "150",
        },
        {
            "State": "West Bengal",
            "District": "Nadia",
            "Market": "Krishnanagar",
            "Commodity": "Tomato",
            "Variety": "Local",
            "Grade": "A",
            "Date": "03/09/2026",
            "Modal_Price": "1950",
            "Arrival_Quantity": "140",
        },
    ]

    df = market_records_to_dataframe(records)

    assert isinstance(df, pd.DataFrame)

    assert list(df.columns) == [
        "State",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade",
        "Date",
        "Modal_Price",
        "Arrival_Quantity",
    ]

    assert len(df) == 2

    assert pd.api.types.is_datetime64_any_dtype(
        df["Date"]
    )

    assert df["Modal_Price"].dtype.kind in "fi"

    assert df["Arrival_Quantity"].dtype.kind in "fi"

    assert df.iloc[0]["Date"] < df.iloc[1]["Date"]


def test_market_records_to_dataframe_rejects_empty_records():
    with pytest.raises(ValueError, match="records cannot be empty"):
        market_records_to_dataframe([])


def test_market_records_to_dataframe_rejects_missing_columns():
    records = [
        {
            "State": "West Bengal",
            "District": "Nadia",
            "Market": "Krishnanagar",
            "Commodity": "Tomato",
        }
    ]

    with pytest.raises(
        ValueError,
        match="Missing required forecast columns",
    ):
        market_records_to_dataframe(records)


def test_market_records_to_dataframe_removes_invalid_rows():
    records = [
        {
            "State": "West Bengal",
            "District": "Nadia",
            "Market": "Krishnanagar",
            "Commodity": "Tomato",
            "Variety": "Local",
            "Grade": "A",
            "Date": "04/09/2026",
            "Modal_Price": "2000",
            "Arrival_Quantity": "150",
        },
        {
            "State": "West Bengal",
            "District": "Nadia",
            "Market": "Krishnanagar",
            "Commodity": "Tomato",
            "Variety": "Local",
            "Grade": "A",
            "Date": "invalid-date",
            "Modal_Price": "2100",
            "Arrival_Quantity": "160",
        },
    ]

    df = market_records_to_dataframe(records)

    assert len(df) == 1
    assert df.iloc[0]["Modal_Price"] == 2000

def test_forecast_from_market_records():
    records = [
        {
            "State": "West Bengal",
            "District": "Nadia",
            "Market": "Krishnanagar",
            "Commodity": "Tomato",
            "Variety": "Local",
            "Grade": "A",
            "Date": "01/09/2026",
            "Modal_Price": 1900,
            "Arrival_Quantity": 120,
        },
        {
            "State": "West Bengal",
            "District": "Nadia",
            "Market": "Krishnanagar",
            "Commodity": "Tomato",
            "Variety": "Local",
            "Grade": "A",
            "Date": "02/09/2026",
            "Modal_Price": 1950,
            "Arrival_Quantity": 130,
        },
    ]

    fake_forecast = {
        "predicted_price": 2000.0,
        "forecast_date": "03/09/2026",
    }

    with patch(
        "src.data_access.forecast_data.predict_price"
    ) as mock_predict:

        mock_predict.return_value.model_dump.return_value = (
            fake_forecast
        )

        result = forecast_from_market_records(records)

        assert result == fake_forecast

        mock_predict.assert_called_once()

        historical_data = (
            mock_predict.call_args.kwargs["historical_data"]
        )

        assert isinstance(historical_data, pd.DataFrame)

        assert len(historical_data) == 2

        assert list(historical_data.columns) == [
            "State",
            "District",
            "Market",
            "Commodity",
            "Variety",
            "Grade",
            "Date",
            "Modal_Price",
            "Arrival_Quantity",
        ]    


def test_forecast_from_market_records_with_real_predictor():
    dates = pd.date_range(
        start="2026-07-01",
        periods=40,
        freq="D",
    )

    records = []

    for i, date in enumerate(dates):
        records.append(
            {
                "State": "West Bengal",
                "District": "Nadia",
                "Market": "Krishnanagar",
                "Commodity": "Tomato",
                "Variety": "Local",
                "Grade": "A",
                "Date": date.strftime("%d/%m/%Y"),
                "Modal_Price": 1800 + (i * 10),
                "Arrival_Quantity": 100 + i,
            }
        )

    result = forecast_from_market_records(records)

    assert isinstance(result, dict)

    assert "predicted_price" in result

    assert result["predicted_price"] >= 0        