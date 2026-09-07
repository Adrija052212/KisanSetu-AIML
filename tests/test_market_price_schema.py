from datetime import date

import pytest

from src.schemas.market_price import MarketPrice


def test_valid_market_price():
    price = MarketPrice(
        Date="2026-09-05",
        State="West Bengal",
        District="North 24 Parganas",
        Market="Barasat",
        Commodity_Group="Vegetables",
        Commodity="Onion",
        Variety="Red Onion",
        Grade="A",
        Min_Price=2200,
        Max_Price=2800,
        Modal_Price=2500,
        Price_Unit="Rs./Quintal",
        Arrival_Quantity=120,
        Arrival_Unit="Quintal",
    )

    assert price.date == date(2026, 9, 5)
    assert price.commodity == "Onion"
    assert price.modal_price == 2500
    assert price.market == "Barasat"


def test_python_field_names_are_supported():
    price = MarketPrice(
        date="2026-09-05",
        state="West Bengal",
        district="Kolkata",
        market="Koley Market",
        commodity="Potato",
        min_price=1800,
        max_price=2200,
        modal_price=2000,
    )

    assert price.state == "West Bengal"
    assert price.commodity == "Potato"
    assert price.modal_price == 2000


def test_negative_price_is_invalid():
    with pytest.raises(ValueError):
        MarketPrice(
            Date="2026-09-05",
            State="West Bengal",
            District="Kolkata",
            Market="Koley Market",
            Commodity="Potato",
            Min_Price=-100,
            Max_Price=2200,
            Modal_Price=2000,
        )


def test_default_values():
    price = MarketPrice(
        Date="2026-09-05",
        State="West Bengal",
        District="Kolkata",
        Market="Koley Market",
        Commodity="Potato",
        Min_Price=1800,
        Max_Price=2200,
        Modal_Price=2000,
    )

    assert price.grade == "Unknown"
    assert price.price_unit == "Rs./Quintal"
    assert price.variety is None
    assert price.arrival_quantity is None


def test_date_conversion():
    price = MarketPrice(
        Date="2026-09-05",
        State="West Bengal",
        District="Kolkata",
        Market="Koley Market",
        Commodity="Tomato",
        Min_Price=1500,
        Max_Price=1900,
        Modal_Price=1700,
    )

    assert isinstance(price.date, date)
    assert price.date == date(2026, 9, 5)