from datetime import date

from src.data.market_price_converter import dataframe_row_to_market_price
from src.schemas import MarketPrice


def test_dataframe_row_conversion():
    row = {
        "Date": "2026-09-05",
        "State": "West Bengal",
        "District": "North 24 Parganas",
        "Market": "Barasat",
        "Commodity_Group": "Vegetables",
        "Commodity": "Onion",
        "Variety": "Red Onion",
        "Grade": "A",
        "Min_Price": 2200,
        "Max_Price": 2800,
        "Modal_Price": 2500,
        "Price_Unit": "Rs./Quintal",
        "Arrival_Quantity": 120,
        "Arrival_Unit": "Quintal",
    }

    result = dataframe_row_to_market_price(row)

    assert isinstance(result, MarketPrice)
    assert result.date == date(2026, 9, 5)
    assert result.commodity == "Onion"
    assert result.modal_price == 2500
    assert result.market == "Barasat"


def test_optional_fields_are_handled():
    row = {
        "Date": "2026-09-05",
        "State": "West Bengal",
        "District": "Kolkata",
        "Market": "Koley Market",
        "Commodity": "Potato",
        "Min_Price": 1800,
        "Max_Price": 2200,
        "Modal_Price": 2000,
    }

    result = dataframe_row_to_market_price(row)

    assert result.commodity == "Potato"
    assert result.variety is None
    assert result.commodity_group is None
    assert result.grade == "Unknown"
    assert result.price_unit == "Rs./Quintal"