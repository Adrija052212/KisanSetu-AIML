from typing import Any, Dict, List

from src.services.matching_service import (
    find_best_buyers,
    find_best_farmers,
)


def best_buyers_tool(
    farmer_lot: Dict[str, Any],
    buyers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Find and rank the best buyers for a farmer's lot.
    """
    if not buyers:
        raise ValueError("buyers cannot be empty.")

    return find_best_buyers(
        farmer_lot=farmer_lot,
        buyers=buyers,
    )


def best_farmers_tool(
    buyer_requirement: Dict[str, Any],
    farmers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Find and rank the best farmer lots for a buyer requirement.
    """
    if not farmers:
        raise ValueError("farmers cannot be empty.")

    return find_best_farmers(
        buyer_requirement=buyer_requirement,
        farmers=farmers,
    )

