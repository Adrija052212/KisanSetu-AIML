from typing import Dict, List, Union

from src.schemas import FarmerLot, BuyerRequirement
from src.matching.filters import filter_farmers
from src.matching.scoring import calculate_farmer_match_score


def match_farmers(
    buyer_requirement: Union[BuyerRequirement, Dict],
    farmers: List[Union[FarmerLot, Dict]]
) -> Dict:
    """
    Find and rank the best farmer lots for a buyer requirement.
    """

    if not farmers:
        raise ValueError("farmers cannot be empty.")

    # Convert Pydantic model to dictionary if necessary
    if isinstance(buyer_requirement, BuyerRequirement):
        buyer_requirement = buyer_requirement.model_dump()

    # Normalize farmer records
    normalized_farmers = []

    for farmer in farmers:
        if isinstance(farmer, FarmerLot):
            normalized_farmers.append(farmer.model_dump())
        else:
            normalized_farmers.append(farmer)

    # Step 1: Filter compatible farmers
    compatible_farmers = filter_farmers(
        buyer_requirement,
        normalized_farmers
    )

    # No compatible farmers
    if not compatible_farmers:
        return {
            "buyer_requirement": buyer_requirement,
            "best_farmer": None,
            "matches": []
        }

    # Step 2: Score compatible farmers
    scored_farmers = []

    for farmer in compatible_farmers:
        score = calculate_farmer_match_score(
            buyer_requirement,
            farmer
        )

        scored_farmers.append({
            "farmer_id": farmer["farmer_id"],
            "lot_id": farmer["lot_id"],
            "commodity": farmer["commodity"],
            "quantity": farmer["quantity"],
            "grade": farmer["grade"],
            "location": farmer["location"],
            "expected_price": farmer.get("expected_price"),
            **score
        })

    # Step 3: Rank highest score first
    ranked_farmers = sorted(
        scored_farmers,
        key=lambda x: x["match_score"],
        reverse=True
    )

    # Add rank
    for rank, farmer in enumerate(ranked_farmers, start=1):
        farmer["rank"] = rank

    return {
        "buyer_requirement": buyer_requirement,
        "best_farmer": ranked_farmers[0],
        "matches": ranked_farmers
    }