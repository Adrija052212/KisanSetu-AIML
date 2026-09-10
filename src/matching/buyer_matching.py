from typing import Dict, List, Union

from src.matching.filters import filter_buyers
from src.matching.scoring import (
    calculate_match_score,
    score_buyers,
    rank_buyers,
)
from src.schemas import FarmerLot, BuyerRequirement


def match_buyers(
    farmer_lot: Union[FarmerLot, Dict],
    buyers: List[Union[BuyerRequirement, Dict]],
) -> Dict:

    if not buyers:
        raise ValueError("buyers cannot be empty.")

    # Convert Pydantic models to dictionaries.
    if isinstance(farmer_lot, FarmerLot):
        farmer_lot = farmer_lot.model_dump()

    normalized_buyers = []

    for buyer in buyers:
        if isinstance(buyer, BuyerRequirement):
            normalized_buyers.append(buyer.model_dump())
        else:
            normalized_buyers.append(buyer)

    compatible_buyers = filter_buyers(
        farmer_lot,
        normalized_buyers
    )

    if not compatible_buyers:
        return {
            "farmer_lot": farmer_lot,
            "best_buyer": None,
            "matches": [],
        }

    scored_buyers = score_buyers(
        farmer_lot,
        compatible_buyers
    )

    ranked_buyers = rank_buyers(scored_buyers)

    return {
        "farmer_lot": farmer_lot,
        "best_buyer": ranked_buyers[0],
        "matches": ranked_buyers,
    }