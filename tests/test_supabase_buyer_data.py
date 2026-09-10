from src.data_access.buyer_data import get_open_buyer_requirements


def test_get_open_buyer_requirements_from_supabase():
    requirements = get_open_buyer_requirements(
        commodity="Tomato",
        limit=10,
    )

    assert isinstance(requirements, list)

    if requirements:
        requirement = requirements[0]

        assert requirement.get("buyer_id") is not None
        assert requirement.get("crop_name", "").lower() == "tomato"

        # buyer_profile should be attached by buyer_data.py
        assert "buyer_profile" in requirement