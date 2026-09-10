from unittest.mock import patch

import pytest

from src.services.price_service import (
    forecast_market_series,
)


def test_forecast_market_series():
    mock_records = [
        {
            "State": "West Bengal",
            "District": "Nadia",
            "Market": "Krishnanagar",
            "Commodity": "Tomato",
            "Variety": "Local",
            "Grade": "A",
            "Date": "04/09/2026",
            "Modal_Price": 2000,
            "Arrival_Quantity": 150,
        }
    ]

    fake_forecast = {
        "predicted_price": 2050.0,
        "forecast_date": "05/09/2026",
    }

    with patch(
        "src.services.price_service.get_market_price_history"
    ) as mock_history, patch(
        "src.services.price_service.forecast_from_market_records"
    ) as mock_forecast:

        mock_history.return_value = mock_records
        mock_forecast.return_value = fake_forecast

        result = forecast_market_series(
            state="West Bengal",
            district="Nadia",
            market="Krishnanagar",
            commodity="Tomato",
            variety="Local",
            grade="A",
        )

        assert result == fake_forecast

        mock_history.assert_called_once_with(
            state="West Bengal",
            district="Nadia",
            market="Krishnanagar",
            commodity="Tomato",
            variety="Local",
            grade="A",
        )

        mock_forecast.assert_called_once_with(
            mock_records
        )

def test_forecast_market_series_no_history():
    with patch(
        "src.services.price_service.get_market_price_history"
    ) as mock_history:

        mock_history.return_value = []

        with pytest.raises(
            ValueError,
            match="No historical market data found",
        ):
            forecast_market_series(
                state="West Bengal",
                district="Nadia",
                market="Krishnanagar",
                commodity="Tomato",
                variety="Local",
                grade="A",
            )
