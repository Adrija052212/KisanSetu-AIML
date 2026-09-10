from typing import Any, Dict

from src.services.buyer_service import get_best_buyers
from src.services.farmer_service import get_best_farmers


def best_buyers_tool(
    commodity: str,
    quantity: float,
    grade: str,
    location: str,
    variety: str = None,
    expected_price: float = None,
) -> Dict[str, Any]:
    """Find and rank the best buyers for a farmer's produce
    using live buyer requirements from Supabase."""
    return get_best_buyers(
        commodity=commodity,
        quantity=quantity,
        grade=grade,
        location=location,
        variety=variety,
        expected_price=expected_price,
    )


def best_farmers_tool(
    commodity: str,
    required_quantity: float,
    grade: str,
    location: str,
    variety: str = None,
    offered_price: float = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Find and rank the best farmer lots for a buyer requirement
    using active farmer listings from Supabase."""
    return get_best_farmers(
        commodity=commodity,
        required_quantity=required_quantity,
        grade=grade,
        location=location,
        variety=variety,
        offered_price=offered_price,
        limit=limit,
    )