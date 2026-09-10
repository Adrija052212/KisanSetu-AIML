from src.matching.scoring import calculate_farmer_match_score
from src.matching.farmer_matching import match_farmers

def test_perfect_farmer_match():
    buyer = {
        "commodity": "Tomato",
        "required_quantity": 50,
        "grade": "A",
        "location": "Nadia",
        "offered_price": 2300
    }

    farmer = {
        "farmer_id": "F001",
        "lot_id": "L001",
        "commodity": "Tomato",
        "quantity": 50,
        "grade": "A",
        "location": "Nadia",
        "expected_price": 2200
    }

    result = calculate_farmer_match_score(
        buyer,
        farmer
    )

    assert result["match_score"] == 100
    assert result["match_level"] == "Excellent"


def test_partial_quantity_match():
    buyer = {
        "commodity": "Tomato",
        "required_quantity": 100,
        "grade": "A",
        "location": "Nadia",
        "offered_price": 2300
    }

    farmer = {
        "farmer_id": "F001",
        "lot_id": "L001",
        "commodity": "Tomato",
        "quantity": 50,
        "grade": "A",
        "location": "Nadia",
        "expected_price": 2200
    }

    result = calculate_farmer_match_score(
        buyer,
        farmer
    )

    assert result["quantity_score"] == 10
    assert result["match_score"] == 90


def test_any_grade():
    buyer = {
        "commodity": "Tomato",
        "required_quantity": 50,
        "grade": "Any",
        "location": "Nadia",
        "offered_price": 2300
    }

    farmer = {
        "farmer_id": "F001",
        "lot_id": "L001",
        "commodity": "Tomato",
        "quantity": 50,
        "grade": "B",
        "location": "Nadia",
        "expected_price": 2200
    }

    result = calculate_farmer_match_score(
        buyer,
        farmer
    )

    assert result["grade_score"] == 15


def test_different_location():
    buyer = {
        "commodity": "Tomato",
        "required_quantity": 50,
        "grade": "A",
        "location": "Nadia",
        "offered_price": 2300
    }

    farmer = {
        "farmer_id": "F001",
        "lot_id": "L001",
        "commodity": "Tomato",
        "quantity": 50,
        "grade": "A",
        "location": "Kolkata",
        "expected_price": 2200
    }

    result = calculate_farmer_match_score(
        buyer,
        farmer
    )

    assert result["location_score"] == 5

def test_farmer_matching_returns_best_farmer():

    buyer = {
        "buyer_id": "B001",
        "requirement_id": "R001",
        "commodity": "Tomato",
        "variety": "Local",
        "required_quantity": 50,
        "quantity_unit": "Quintal",
        "grade": "A",
        "location": "Nadia",
        "offered_price": 2300,
        "required_by_date": "2026-09-08"
    }

    farmers = [
        {
            "farmer_id": "F001",
            "lot_id": "L001",
            "commodity": "Tomato",
            "variety": "Local",
            "quantity": 50,
            "quantity_unit": "Quintal",
            "grade": "A",
            "location": "Nadia",
            "expected_price": 2200,
            "available_date": "2026-09-06"
        },
        {
            "farmer_id": "F002",
            "lot_id": "L002",
            "commodity": "Tomato",
            "variety": "Local",
            "quantity": 30,
            "quantity_unit": "Quintal",
            "grade": "A",
            "location": "Kolkata",
            "expected_price": 2200,
            "available_date": "2026-09-06"
        },
        {
            "farmer_id": "F003",
            "lot_id": "L003",
            "commodity": "Potato",
            "variety": "Local",
            "quantity": 50,
            "quantity_unit": "Quintal",
            "grade": "A",
            "location": "Nadia",
            "expected_price": 2000,
            "available_date": "2026-09-06"
        }
    ]

    result = match_farmers(
        buyer_requirement=buyer,
        farmers=farmers
    )

    assert result["best_farmer"]["farmer_id"] == "F001"
    assert result["best_farmer"]["match_score"] == 100

    assert len(result["matches"]) == 2
    assert result["matches"][0]["farmer_id"] == "F001"
    assert result["matches"][1]["farmer_id"] == "F002"


def test_wrong_commodity_is_filtered():

    buyer = {
        "commodity": "Tomato",
        "required_quantity": 50,
        "grade": "A",
        "location": "Nadia",
        "offered_price": 2300
    }

    farmers = [
        {
            "farmer_id": "F001",
            "lot_id": "L001",
            "commodity": "Potato",
            "quantity": 50,
            "grade": "A",
            "location": "Nadia",
            "expected_price": 2000
        }
    ]

    result = match_farmers(
        buyer_requirement=buyer,
        farmers=farmers
    )

    assert result["best_farmer"] is None
    assert result["matches"] == []


def test_farmer_ranking():

    buyer = {
        "commodity": "Tomato",
        "required_quantity": 50,
        "grade": "A",
        "location": "Nadia",
        "offered_price": 2300
    }

    farmers = [
        {
            "farmer_id": "F001",
            "lot_id": "L001",
            "commodity": "Tomato",
            "quantity": 40,
            "grade": "A",
            "location": "Kolkata",
            "expected_price": 2300
        },
        {
            "farmer_id": "F002",
            "lot_id": "L002",
            "commodity": "Tomato",
            "quantity": 50,
            "grade": "A",
            "location": "Nadia",
            "expected_price": 2200
        }
    ]

    result = match_farmers(
        buyer_requirement=buyer,
        farmers=farmers
    )

    assert result["matches"][0]["farmer_id"] == "F002"
    assert result["matches"][0]["rank"] == 1    