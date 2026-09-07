from typing import Dict, List


def calculate_match_score(
    farmer_lot: Dict,
    buyer: Dict
) -> Dict:
    """
    Calculate a compatibility score between a farmer's lot
    and a buyer's requirement.

    Score components:
        Commodity : 30%
        Quantity  : 20%
        Grade     : 15%
        Location  : 15%
        Price     : 20%

    Returns
    -------
    Dict
        Detailed matching score.
    """

    # --------------------------------------------------
    # Validate required fields
    # --------------------------------------------------

    farmer_required = [
        "commodity",
        "quantity",
        "grade",
        "location"
    ]

    buyer_required = [
        "commodity",
        "required_quantity",
        "grade",
        "location",
        "offered_price"
    ]

    for field in farmer_required:
        if field not in farmer_lot:
            raise ValueError(
                f"Farmer lot is missing '{field}'."
            )

    for field in buyer_required:
        if field not in buyer:
            raise ValueError(
                f"Buyer is missing '{field}'."
            )

    farmer_quantity = float(
        farmer_lot["quantity"]
    )

    required_quantity = float(
        buyer["required_quantity"]
    )

    offered_price = float(
        buyer["offered_price"]
    )

    if farmer_quantity <= 0:
        raise ValueError(
            "Farmer quantity must be greater than zero."
        )

    if required_quantity <= 0:
        raise ValueError(
            "Buyer required quantity must be greater than zero."
        )

    if offered_price < 0:
        raise ValueError(
            "Buyer offered price cannot be negative."
        )

    # --------------------------------------------------
    # 1. Commodity score — 30%
    # --------------------------------------------------

    farmer_commodity = str(
        farmer_lot["commodity"]
    ).strip().lower()

    buyer_commodity = str(
        buyer["commodity"]
    ).strip().lower()

    commodity_score = (
        30.0
        if farmer_commodity == buyer_commodity
        else 0.0
    )

    # --------------------------------------------------
    # 2. Quantity score — 20%
    # --------------------------------------------------

    if farmer_quantity >= required_quantity:
        quantity_score = 20.0
    else:
        quantity_ratio = (
            farmer_quantity / required_quantity
        )

        quantity_score = 20.0 * quantity_ratio

    # --------------------------------------------------
    # 3. Grade score — 15%
    # --------------------------------------------------

    farmer_grade = str(
        farmer_lot["grade"]
    ).strip().lower()

    buyer_grade = str(
        buyer["grade"]
    ).strip().lower()

    if farmer_grade == buyer_grade:
        grade_score = 15.0

    elif buyer_grade in {
        "any",
        "all",
        "any grade"
    }:
        grade_score = 15.0

    else:
        grade_score = 0.0

    # --------------------------------------------------
    # 4. Location score — 15%
    # --------------------------------------------------

    farmer_location = str(
        farmer_lot["location"]
    ).strip().lower()

    buyer_location = str(
        buyer["location"]
    ).strip().lower()

    if farmer_location == buyer_location:
        location_score = 15.0
    else:
        location_score = 5.0

    # --------------------------------------------------
    # 5. Price score — 20%
    # --------------------------------------------------

    farmer_expected_price = farmer_lot.get(
        "expected_price"
    )

    if farmer_expected_price is None:
        price_score = 20.0

    else:
        farmer_expected_price = float(
            farmer_expected_price
        )

        if farmer_expected_price < 0:
            raise ValueError(
                "Farmer expected price cannot be negative."
            )

        if farmer_expected_price == 0:
            price_score = 20.0

        elif offered_price >= farmer_expected_price:
            price_score = 20.0

        else:
            price_ratio = (
                offered_price /
                farmer_expected_price
            )

            price_score = max(
                0.0,
                min(
                    20.0,
                    20.0 * price_ratio
                )
            )

    # --------------------------------------------------
    # Total score
    # --------------------------------------------------

    total_score = (
        commodity_score
        + quantity_score
        + grade_score
        + location_score
        + price_score
    )

    # --------------------------------------------------
    # Match classification
    # --------------------------------------------------

    if total_score >= 80:
        match_level = "Excellent"

    elif total_score >= 60:
        match_level = "Good"

    elif total_score >= 40:
        match_level = "Moderate"

    else:
        match_level = "Poor"

    return {
        "commodity_score": round(
            commodity_score,
            2
        ),
        "quantity_score": round(
            quantity_score,
            2
        ),
        "grade_score": round(
            grade_score,
            2
        ),
        "location_score": round(
            location_score,
            2
        ),
        "price_score": round(
            price_score,
            2
        ),
        "match_score": round(
            total_score,
            2
        ),
        "match_level": match_level,
    }


def score_buyers(
    farmer_lot: Dict,
    buyers: List[Dict]
) -> List[Dict]:
    """
    Calculate match scores for a list of buyers.

    Parameters
    ----------
    farmer_lot : Dict
        Farmer's lot information.

    buyers : List[Dict]
        Buyers that have already passed
        the compatibility filters.

    Returns
    -------
    List[Dict]
        Buyers with their calculated match scores.
    """

    if not buyers:
        return []

    scored_buyers = []

    for buyer in buyers:

        score = calculate_match_score(
            farmer_lot,
            buyer
        )

        scored_buyers.append(
            {
                "buyer_id": buyer.get(
                    "buyer_id"
                ),
                "buyer_name": buyer.get(
                    "buyer_name",
                    "Unknown Buyer"
                ),
                "offered_price": buyer[
                    "offered_price"
                ],
                **score,
            }
        )

    return scored_buyers


def rank_buyers(
    scored_buyers: List[Dict]
) -> List[Dict]:
    """
    Rank buyers from highest match score
    to lowest match score.
    """

    if not scored_buyers:
        return []

    ranked_buyers = sorted(
        scored_buyers,
        key=lambda buyer: buyer["match_score"],
        reverse=True
    )

    for rank, buyer in enumerate(
        ranked_buyers,
        start=1
    ):
        buyer["rank"] = rank

    return ranked_buyers

def calculate_farmer_match_score(
    buyer_requirement: Dict,
    farmer: Dict
) -> Dict:
    """
    Calculate how well a farmer lot matches a buyer requirement.

    Score:
        Commodity: 30
        Quantity: 20
        Grade: 15
        Location: 15
        Price: 20

    Maximum score = 100.
    """

    # --------------------------------------------------
    # 1. Commodity score
    # --------------------------------------------------
    buyer_commodity = str(
        buyer_requirement["commodity"]
    ).strip().lower()

    farmer_commodity = str(
        farmer["commodity"]
    ).strip().lower()

    commodity_score = (
        30
        if buyer_commodity == farmer_commodity
        else 0
    )

    # --------------------------------------------------
    # 2. Quantity score
    # --------------------------------------------------
    required_quantity = float(
        buyer_requirement["required_quantity"]
    )

    farmer_quantity = float(
        farmer["quantity"]
    )

    if farmer_quantity >= required_quantity:
        quantity_score = 20
    else:
        quantity_score = (
            farmer_quantity / required_quantity
        ) * 20

    # --------------------------------------------------
    # 3. Grade score
    # --------------------------------------------------
    buyer_grade = str(
        buyer_requirement.get("grade", "Any")
    ).strip().lower()

    farmer_grade = str(
        farmer.get("grade", "Unknown")
    ).strip().lower()

    accepted_grades = {
        "any",
        "all",
        "any grade"
    }

    if (
        buyer_grade in accepted_grades
        or buyer_grade == farmer_grade
    ):
        grade_score = 15
    else:
        grade_score = 0

    # --------------------------------------------------
    # 4. Location score
    # --------------------------------------------------
    buyer_location = str(
        buyer_requirement["location"]
    ).strip().lower()

    farmer_location = str(
        farmer["location"]
    ).strip().lower()

    if buyer_location == farmer_location:
        location_score = 15
    else:
        location_score = 5

    # --------------------------------------------------
    # 5. Price score
    # --------------------------------------------------
    offered_price = float(
        buyer_requirement["offered_price"]
    )

    expected_price = farmer.get("expected_price")

    # Farmer has no expected price
    if expected_price is None or float(expected_price) == 0:
        price_score = 20

    # Buyer offers at least the farmer's expected price
    elif offered_price >= float(expected_price):
        price_score = 20

    # Buyer offers less than farmer's expected price
    else:
        price_score = (
            offered_price / float(expected_price)
        ) * 20

    # --------------------------------------------------
    # Total score
    # --------------------------------------------------
    match_score = (
        commodity_score
        + quantity_score
        + grade_score
        + location_score
        + price_score
    )

    match_score = round(
        min(match_score, 100),
        2
    )

    # --------------------------------------------------
    # Match level
    # --------------------------------------------------
    if match_score >= 80:
        match_level = "Excellent"
    elif match_score >= 60:
        match_level = "Good"
    elif match_score >= 40:
        match_level = "Moderate"
    else:
        match_level = "Poor"

    return {
        "commodity_score": commodity_score,
        "quantity_score": round(quantity_score, 2),
        "grade_score": grade_score,
        "location_score": location_score,
        "price_score": round(price_score, 2),
        "match_score": match_score,
        "match_level": match_level
    }    