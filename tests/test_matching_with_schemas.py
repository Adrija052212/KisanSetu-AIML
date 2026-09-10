from src.matching.buyer_matching import match_buyers
from src.schemas import BuyerRequirement, FarmerLot


def test_matching_with_pydantic_schemas():
    farmer_lot = FarmerLot(
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

    buyers = [
        BuyerRequirement(
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
        ),
        BuyerRequirement(
            buyer_id="B205",
            requirement_id="REQ902",
            commodity="Onion",
            variety="Red Onion",
            required_quantity=30,
            quantity_unit="Quintal",
            grade="A",
            location="Pune",
            offered_price=2600,
            required_by_date="2026-09-09",
        ),
    ]

    result = match_buyers(farmer_lot, buyers)

    assert result["best_buyer"] is not None
    assert result["best_buyer"]["buyer_id"] == "B204"
    assert len(result["matches"]) == 2