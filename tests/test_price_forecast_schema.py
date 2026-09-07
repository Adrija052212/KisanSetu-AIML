from datetime import date

import pytest

from src.schemas.price_forecast import PriceForecast


def test_valid_price_forecast():
    forecast = PriceForecast(
        series_id="MH_Nashik_Nashik_Onion_Red_A",
        commodity="Onion",
        variety="Red Onion",
        grade="A",
        market="Nashik",
        forecast_date="2026-09-08",
        predicted_price=2785.50,
        model_version="baseline_v1",
    )

    assert forecast.series_id == "MH_Nashik_Nashik_Onion_Red_A"
    assert forecast.commodity == "Onion"
    assert forecast.predicted_price == 2785.50
    assert forecast.model_version == "baseline_v1"


def test_forecast_date_is_converted_to_date():
    forecast = PriceForecast(
        series_id="WB_Kolkata_Koley_Tomato_Local_A",
        commodity="Tomato",
        market="Koley Market",
        forecast_date="2026-09-08",
        predicted_price=1800,
        model_version="baseline_v1",
    )

    assert isinstance(forecast.forecast_date, date)
    assert forecast.forecast_date == date(2026, 9, 8)


def test_negative_predicted_price_is_invalid():
    with pytest.raises(ValueError):
        PriceForecast(
            series_id="MH_Nashik_Nashik_Onion_Red_A",
            commodity="Onion",
            market="Nashik",
            forecast_date="2026-09-08",
            predicted_price=-500,
            model_version="baseline_v1",
        )


def test_default_grade():
    forecast = PriceForecast(
        series_id="WB_Kolkata_Koley_Potato_Local",
        commodity="Potato",
        market="Koley Market",
        forecast_date="2026-09-08",
        predicted_price=2000,
        model_version="baseline_v1",
    )

    assert forecast.grade == "Unknown"
    assert forecast.variety is None


def test_model_version_is_required():
    with pytest.raises(ValueError):
        PriceForecast(
            series_id="MH_Nashik_Nashik_Onion_Red_A",
            commodity="Onion",
            market="Nashik",
            forecast_date="2026-09-08",
            predicted_price=2785,
        )