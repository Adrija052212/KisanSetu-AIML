from datetime import date

import pytest

from src.schemas.buyer_requirement import BuyerRequirement


def test_valid_buyer_requirement():
    buyer = BuyerRequirement(
        buyer_id="B204",
        requirement_id="REQ901",
        commodity="Onion",
        variety="Red Onion",
        required_quantity=40,
        quantity_unit="Quintal",
        grade="A",
        location="Mumbai",
        offered_price=2700,
        required_by_date="2026-09-08",
    )

    assert buyer.buyer_id == "B204"
    assert buyer.requirement_id == "REQ901"
    assert buyer.commodity == "Onion"
    assert buyer.required_quantity == 40
    assert buyer.offered_price == 2700


def test_required_quantity_must_be_positive():
    with pytest.raises(ValueError):
        BuyerRequirement(
            buyer_id="B204",
            requirement_id="REQ901",
            commodity="Onion",
            required_quantity=0,
            location="Mumbai",
            offered_price=2700,
            required_by_date="2026-09-08",
        )


def test_negative_offered_price_is_invalid():
    with pytest.raises(ValueError):
        BuyerRequirement(
            buyer_id="B204",
            requirement_id="REQ901",
            commodity="Onion",
            required_quantity=40,
            location="Mumbai",
            offered_price=-100,
            required_by_date="2026-09-08",
        )


def test_default_values():
    buyer = BuyerRequirement(
        buyer_id="B204",
        requirement_id="REQ901",
        commodity="Potato",
        required_quantity=20,
        location="Kolkata",
        offered_price=2000,
        required_by_date="2026-09-08",
    )

    assert buyer.quantity_unit == "Quintal"
    assert buyer.grade == "Any"
    assert buyer.variety is None


def test_date_is_converted_to_date_object():
    buyer = BuyerRequirement(
        buyer_id="B204",
        requirement_id="REQ901",
        commodity="Tomato",
        required_quantity=10,
        location="Kolkata",
        offered_price=1800,
        required_by_date="2026-09-08",
    )

    assert buyer.required_by_date == date(2026, 9, 8)