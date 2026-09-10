from typing import Dict, List, Optional

from src.data_access.farmer_data import (
    get_active_farmer_listings,
)
from src.matching.farmer_matching import match_farmers


def _to_float(value):
    """
    Safely convert a value to float.
    Returns None when conversion is not possible.
    """

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _quantity_to_quintal(
    quantity: float,
    unit: Optional[str],
) -> float:
    """
    Convert farmer quantity to quintals.

    1 quintal = 100 kg
    1 tonne = 10 quintals
    """

    normalized_unit = (
        str(unit).strip().lower()
        if unit
        else "quintal"
    )

    if normalized_unit in {
        "kg",
        "kilogram",
        "kilograms",
    }:
        return quantity / 100

    if normalized_unit in {
        "tonne",
        "ton",
        "tons",
        "tonnes",
    }:
        return quantity * 10

    if normalized_unit in {
        "quintal",
        "quintals",
        "q",
    }:
        return quantity

    raise ValueError(
        f"Unsupported farmer quantity unit: {unit}"
    )


def _price_to_quintal(
    price: float,
    unit: Optional[str],
) -> float:
    """
    Convert farmer expected price to Rs./Quintal.

    1 quintal = 100 kg
    1 tonne = 10 quintals
    """

    normalized_unit = (
        str(unit).strip().lower()
        if unit
        else "quintal"
    )

    if normalized_unit in {
        "kg",
        "kilogram",
        "kilograms",
    }:
        return price * 100

    if normalized_unit in {
        "tonne",
        "ton",
        "tons",
        "tonnes",
    }:
        return price / 10

    if normalized_unit in {
        "quintal",
        "quintals",
        "q",
    }:
        return price

    raise ValueError(
        f"Unsupported farmer price unit: {unit}"
    )


def _normalize_farmer_listing(
    listing: Dict,
) -> Optional[Dict]:
    """
    Convert a Supabase produce listing into the
    dictionary format expected by farmer_matching.py.
    """

    farmer_id = listing.get("farmer_id")
    lot_id = listing.get("id")
    commodity = listing.get("crop_name")

    if not farmer_id or not lot_id or not commodity:
        return None

    # --------------------------------------------------
    # Quantity
    # --------------------------------------------------

    quantity = _to_float(
        listing.get("quantity")
    )

    if quantity is None or quantity <= 0:
        return None

    unit = listing.get("unit") or "quintal"

    quantity = _quantity_to_quintal(
        quantity,
        unit,
    )

    if quantity <= 0:
        return None

    # --------------------------------------------------
    # Expected price
    # --------------------------------------------------

    expected_price = _to_float(
        listing.get("expected_price")
    )

    if expected_price is None or expected_price < 0:
        return None

    expected_price = _price_to_quintal(
        expected_price,
        unit,
    )

    # --------------------------------------------------
    # Normalized farmer
    # --------------------------------------------------

    return {
        "farmer_id": farmer_id,
        "lot_id": lot_id,
        "name": "Unknown Farmer",
        "commodity": commodity,
        "quantity": quantity,
        "grade": listing.get("grade") or "Any",
        "location": listing.get("location") or "Unknown",
        "variety": listing.get("variety"),
        "expected_price": expected_price,
    }


def get_best_farmers(
    commodity: str,
    required_quantity: float,
    grade: str,
    location: str,
    variety: Optional[str] = None,
    offered_price: Optional[float] = None,
    limit: int = 100,
) -> Dict:
    """
    Find and rank farmer lots for a buyer requirement.
    """

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    if not commodity or not commodity.strip():
        raise ValueError(
            "commodity cannot be empty."
        )

    if required_quantity <= 0:
        raise ValueError(
            "required_quantity must be greater than zero."
        )

    if not grade or not grade.strip():
        raise ValueError(
            "grade cannot be empty."
        )

    if not location or not location.strip():
        raise ValueError(
            "location cannot be empty."
        )

    # --------------------------------------------------
    # Fetch active farmer listings
    # --------------------------------------------------

    listings = get_active_farmer_listings(
        commodity=commodity,
        variety=variety,
        grade=grade,
        limit=limit,
    )

    # --------------------------------------------------
    # Normalize listings
    # --------------------------------------------------

    farmers: List[Dict] = []

    for listing in listings:
        farmer = _normalize_farmer_listing(
            listing
        )

        if farmer is not None:
            farmers.append(farmer)

    # --------------------------------------------------
    # Buyer requirement
    # --------------------------------------------------

    buyer_requirement = {
        "commodity": commodity,
        "required_quantity": required_quantity,
        "grade": grade,
        "location": location,
        "variety": variety,
        "offered_price": offered_price,
    }

    # --------------------------------------------------
    # No usable farmer listings
    # --------------------------------------------------

    if not farmers:
        return {
            "buyer_requirement": buyer_requirement,
            "best_farmer": None,
            "matches": [],
        }

    # --------------------------------------------------
    # Existing matching engine
    # --------------------------------------------------

    return match_farmers(
        buyer_requirement=buyer_requirement,
        farmers=farmers,
    )