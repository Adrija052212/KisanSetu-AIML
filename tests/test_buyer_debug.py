from src.data_access.buyer_data import get_open_buyer_requirements


def test_debug_all_buyer_requirements():
    requirements = get_open_buyer_requirements(
        limit=100,
    )

    print("\n========== ALL OPEN BUYER REQUIREMENTS ==========")
    print(f"Total open requirements found: {len(requirements)}")

    for requirement in requirements:
        print("\nRequirement:")
        print("  id:", requirement.get("id"))
        print("  buyer_id:", requirement.get("buyer_id"))
        print("  crop_name:", requirement.get("crop_name"))
        print("  variety:", requirement.get("variety"))
        print("  quantity:", requirement.get("quantity"))
        print("  min_quantity:", requirement.get("min_quantity"))
        print("  max_quantity:", requirement.get("max_quantity"))
        print("  grade:", requirement.get("grade"))
        print("  target_price:", requirement.get("target_price"))
        print("  status:", requirement.get("status"))
        print("  buyer_profile:", requirement.get("buyer_profile"))

    assert isinstance(requirements, list)