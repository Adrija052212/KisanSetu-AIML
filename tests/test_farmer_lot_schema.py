import pytest

from src.schemas.farmer_lot import FarmerLot


def test_valid_farmer_lot():
    lot = FarmerLot(
        farmer_id="F1023",
        lot_id="LOT5001",
        commodity="Onion",
        variety="Red Onion",
        quantity=50,
        quantity_unit="Quintal",
        grade="A",
        location="Nashik",
        expected_price=2500,
        available_date="2026-09-06",
    )

    assert lot.farmer_id == "F1023"
    assert lot.lot_id == "LOT5001"
    assert lot.commodity == "Onion"
    assert lot.quantity == 50
    assert lot.expected_price == 2500


def test_quantity_must_be_positive():
    with pytest.raises(ValueError):
        FarmerLot(
            farmer_id="F1023",
            lot_id="LOT5001",
            commodity="Onion",
            quantity=0,
            location="Nashik",
            available_date="2026-09-06",
        )


def test_negative_expected_price_is_invalid():
    with pytest.raises(ValueError):
        FarmerLot(
            farmer_id="F1023",
            lot_id="LOT5001",
            commodity="Onion",
            quantity=50,
            location="Nashik",
            expected_price=-100,
            available_date="2026-09-06",
        )


def test_default_values():
    lot = FarmerLot(
        farmer_id="F1023",
        lot_id="LOT5001",
        commodity="Potato",
        quantity=20,
        location="Kolkata",
        available_date="2026-09-06",
    )

    assert lot.quantity_unit == "Quintal"
    assert lot.grade == "Unknown"
    assert lot.variety is None
    assert lot.expected_price is None