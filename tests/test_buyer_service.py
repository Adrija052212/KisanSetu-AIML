from src.services import buyer_service


def test_get_best_buyers(monkeypatch):

    fake_requirements = [
        {
            "id": "REQ001",
            "buyer_id": "B001",
            "crop_name": "Tomato",
            "variety": "Local",
            "quantity": 50,
            "min_quantity": 40,
            "max_quantity": 60,
            "grade": "A",
            "target_price": "2400",
            "buyer_profile": {
                "business_name": "FreshMart",
                "preferred_location": "Nadia",
            },
        },
        {
            "id": "REQ002",
            "buyer_id": "B002",
            "crop_name": "Tomato",
            "variety": "Local",
            "quantity": 60,
            "min_quantity": 50,
            "max_quantity": 70,
            "grade": "A",
            "target_price": "2350",
            "buyer_profile": {
                "business_name": "AgroTrade",
                "preferred_location": "Kolkata",
            },
        },
        {
            "id": "REQ003",
            "buyer_id": "B003",
            "crop_name": "Potato",
            "variety": "Local",
            "quantity": 50,
            "min_quantity": 40,
            "max_quantity": 60,
            "grade": "A",
            "target_price": "2500",
            "buyer_profile": {
                "business_name": "PotatoBuyer",
                "preferred_location": "Nadia",
            },
        },
    ]

    def fake_get_open_buyer_requirements(**kwargs):
        return fake_requirements

    monkeypatch.setattr(
        buyer_service,
        "get_open_buyer_requirements",
        fake_get_open_buyer_requirements,
    )

    result = buyer_service.get_best_buyers(
        commodity="Tomato",
        quantity=50,
        grade="A",
        location="Nadia",
        variety="Local",
        expected_price=2300,
    )

    assert result["best_buyer"] is not None

    assert (
        result["best_buyer"]["buyer_id"]
        == "B001"
    )

    assert len(result["matches"]) == 2

    assert (
        result["matches"][0]["buyer_id"]
        == "B001"
    )