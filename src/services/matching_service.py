from typing import Dict, List, Union

from src.matching.buyer_matching import match_buyers
from src.matching.farmer_matching import match_farmers
from src.schemas import FarmerLot, BuyerRequirement


def find_best_buyers(
    farmer_lot: Union[FarmerLot, Dict],
    buyers: List[Union[BuyerRequirement, Dict]],
) -> Dict:
    """
    Find and rank the best buyers for a farmer's lot.
    """

    return match_buyers(
        farmer_lot=farmer_lot,
        buyers=buyers,
    )


def find_best_farmers(
    buyer_requirement: Union[BuyerRequirement, Dict],
    farmers: List[Union[FarmerLot, Dict]],
) -> Dict:
    """
    Find and rank the best farmers for a buyer requirement.
    """

    return match_farmers(
        buyer_requirement=buyer_requirement,
        farmers=farmers,
    )