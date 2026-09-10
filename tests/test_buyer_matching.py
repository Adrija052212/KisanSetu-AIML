from src.matching.buyer_matching import (
    calculate_match_score,
    match_buyers
)


def test_perfect_match():

    farmer_lot = {
        "commodity": "Onion",
        "quantity": 100,
        "grade": "Grade A",
        "location": "Nashik",
        "expected_price": 2500
    }

    buyer = {
        "buyer_id": "B001",
        "buyer_name": "Buyer One",
        "commodity": "Onion",
        "required_quantity": 100,
        "grade": "Grade A",
        "location": "Nashik",
        "offered_price": 2700
    }

    result = calculate_match_score(
        farmer_lot,
        buyer
    )

    assert result["match_score"] == 100
    assert result["match_level"] == "Excellent"


def test_partial_quantity_match():

    farmer_lot = {
        "commodity": "Potato",
        "quantity": 50,
        "grade": "Grade A",
        "location": "Kolkata",
        "expected_price": 2000
    }

    buyer = {
        "commodity": "Potato",
        "required_quantity": 100,
        "grade": "Grade A",
        "location": "Kolkata",
        "offered_price": 2200
    }

    result = calculate_match_score(
        farmer_lot,
        buyer
    )

    assert result["quantity_score"] == 10
    assert result["match_score"] == 90


def test_wrong_commodity():

    farmer_lot = {
        "commodity": "Onion",
        "quantity": 100,
        "grade": "Grade A",
        "location": "Nashik"
    }

    buyer = {
        "commodity": "Potato",
        "required_quantity": 100,
        "grade": "Grade A",
        "location": "Nashik",
        "offered_price": 2500
    }

    result = calculate_match_score(
        farmer_lot,
        buyer
    )

    assert result["commodity_score"] == 0


def test_buyer_ranking():

    farmer_lot = {
        "commodity": "Onion",
        "quantity": 100,
        "grade": "Grade A",
        "location": "Nashik",
        "expected_price": 2500
    }

    buyers = [
        {
            "buyer_id": "B001",
            "buyer_name": "Buyer A",
            "commodity": "Onion",
            "required_quantity": 100,
            "grade": "Grade A",
            "location": "Kolkata",
            "offered_price": 2600
        },
        {
            "buyer_id": "B002",
            "buyer_name": "Buyer B",
            "commodity": "Onion",
            "required_quantity": 100,
            "grade": "Grade A",
            "location": "Nashik",
            "offered_price": 2800
        }
    ]

    result = match_buyers(
        farmer_lot,
        buyers
    )

    assert result["best_buyer"]["buyer_id"] == "B002"
    assert result["matches"][0]["rank"] == 1
    assert result["matches"][1]["rank"] == 2


def test_empty_buyers():

    farmer_lot = {
        "commodity": "Onion",
        "quantity": 100,
        "grade": "Grade A",
        "location": "Nashik"
    }

    try:
        match_buyers(
            farmer_lot,
            []
        )
        assert False
    except ValueError:
        assert True