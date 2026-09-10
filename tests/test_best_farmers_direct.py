import json

from src.mcp.tools.matching import best_farmers_tool


def main():

    buyer_requirement = {
        "commodity": "Tomato",
        "required_quantity": 50,
        "grade": "A",
        "location": "Nadia",
        "variety": "Hybrid",
        "offered_price": 2500,
    }

    farmers = [
        {
            "farmer_id": "F001",
            "lot_id": "L001",
            "name": "Farmer One",
            "commodity": "Tomato",
            "quantity": 70,
            "grade": "A",
            "location": "Nadia",
            "variety": "Hybrid",
            "expected_price": 2400,
        },
        {
            "farmer_id": "F002",
            "lot_id": "L002",
            "name": "Farmer Two",
            "commodity": "Tomato",
            "quantity": 40,
            "grade": "A",
            "location": "Nadia",
            "variety": "Hybrid",
            "expected_price": 2300,
        },
        {
            "farmer_id": "F003",
            "lot_id": "L003",
            "name": "Farmer Three",
            "commodity": "Potato",
            "quantity": 100,
            "grade": "A",
            "location": "Nadia",
            "variety": "Hybrid",
            "expected_price": 2000,
        },
    ]

    try:

        result = best_farmers_tool(
            buyer_requirement=buyer_requirement,
            farmers=farmers,
        )

        print("\n===== DIRECT BEST FARMERS RESULT =====")
        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )
        print("======================================\n")

    except Exception as e:

        print("\n===== ACTUAL ERROR =====")
        print(type(e).__name__)
        print(str(e))
        print("========================\n")

        raise


if __name__ == "__main__":
    main()