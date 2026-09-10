import pandas as pd

from src.mcp.tools.prices import forecast_price_tool


def test_forecast_price_tool_rejects_empty_data():
    try:
        forecast_price_tool([])
        assert False
    except ValueError as exc:
        assert "historical_data cannot be empty" in str(exc)