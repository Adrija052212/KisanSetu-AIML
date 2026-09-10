from typing import Dict, List, Optional

from src.data_access.buyer_data import (
    get_open_buyer_requirements,
)
from src.matching.buyer_matching import match_buyers


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


def _get_buyer_location(profile: Optional[Dict]) -> str:
    """
    Determine the buyer's matching location from
    buyer profile information.
    """
    if not profile:
        return "Unknown"

    preferred_location = profile.get("preferred_location")

    if preferred_location:
        return str(preferred_location)

    city = profile.get("city")
    district = profile.get("district")
    state = profile.get("state")

    location_parts = [
        value
        for value in [city, district, state]
        if value
    ]

    if location_parts:
        return ", ".join(
            str(value)
            for value in location_parts
        )

    return "Unknown"


def _get_buyer_name(profile: Optional[Dict]) -> str:
    """
    Get a display name for the buyer.
    """
    if not profile:
        return "Unknown Buyer"

    business_name = profile.get("business_name")

    if business_name:
        return str(business_name)

    contact_person = profile.get("contact_person")

    if contact_person:
        return str(contact_person)

    return "Unknown Buyer"


def _quantity_to_quintal(
    quantity: float,
    unit: Optional[str],
) -> float:
    """
    Convert a quantity to quintals.

    1 quintal = 100 kg
    1 tonne = 10 quintals
    """
    normalized_unit = (
        str(unit).strip().lower()
        if unit
        else "quintal"
    )

    if normalized_unit in {"kg", "kilogram", "kilograms"}:
        return quantity / 100

    if normalized_unit in {"tonne", "ton", "tons", "tonnes"}:
        return quantity * 10

    if normalized_unit in {"quintal", "quintals", "q"}:
        return quantity

    raise ValueError(
        f"Unsupported buyer quantity unit: {unit}"
    )


def _price_to_quintal(
    price: float,
    unit: Optional[str],
) -> float:
    """
    Convert a buyer target price to Rs./Quintal.

    1 quintal = 100 kg
    1 tonne = 10 quintals
    """
    normalized_unit = (
        str(unit).strip().lower()
        if unit
        else "quintal"
    )

    if normalized_unit in {"kg", "kilogram", "kilograms"}:
        return price * 100

    if normalized_unit in {"tonne", "ton", "tons", "tonnes"}:
        return price / 10

    if normalized_unit in {"quintal", "quintals", "q"}:
        return price

    raise ValueError(
        f"Unsupported buyer price unit: {unit}"
    )


def _normalize_buyer_requirement(
    requirement: Dict,
) -> Optional[Dict]:
    """
    Convert a Supabase buyer requirement into the
    dictionary format expected by the matching engine.

    Quantities and prices are normalized to:
        quantity -> quintals
        price -> Rs./Quintal
    """

    profile = requirement.get("buyer_profile")

    # --------------------------------------------------
    # Unit
    # --------------------------------------------------

    unit = requirement.get("unit") or "quintal"

    # --------------------------------------------------
    # Quantity
    # --------------------------------------------------

    quantity = _to_float(
        requirement.get("quantity")
    )

    min_quantity = _to_float(
        requirement.get("min_quantity")
    )

    max_quantity = _to_float(
        requirement.get("max_quantity")
    )

    if quantity is not None:
        required_quantity = quantity
    elif max_quantity is not None:
        required_quantity = max_quantity
    elif min_quantity is not None:
        required_quantity = min_quantity
    else:
        return None

    required_quantity = _quantity_to_quintal(
        required_quantity,
        unit,
    )

    if required_quantity <= 0:
        return None

    # --------------------------------------------------
    # Offered price
    # --------------------------------------------------

    offered_price = _to_float(
        requirement.get("target_price")
    )

    if offered_price is None:
        return None

    if offered_price < 0:
        return None

    offered_price = _price_to_quintal(
        offered_price,
        unit,
    )

    # --------------------------------------------------
    # Buyer ID
    # --------------------------------------------------

    buyer_id = requirement.get("buyer_id")

    if not buyer_id:
        return None

    # --------------------------------------------------
    # Normalized buyer
    # --------------------------------------------------

    return {
        "buyer_id": buyer_id,
        "buyer_name": _get_buyer_name(profile),
        "commodity": requirement.get("crop_name"),
        "variety": requirement.get("variety"),
        "required_quantity": required_quantity,
        "grade": requirement.get("grade") or "Any",
        "location": _get_buyer_location(profile),
        "offered_price": offered_price,
        "requirement_id": requirement.get("id"),

        # Useful for explaining the result later.
        "original_quantity": quantity,
        "original_unit": unit,
        "original_target_price": _to_float(
            requirement.get("target_price")
        ),
        "price_unit": "Rs./Quintal",
    }


def get_best_buyers(
    commodity: str,
    quantity: float,
    grade: str,
    location: str,
    variety: Optional[str] = None,
    expected_price: Optional[float] = None,
    limit: int = 100,
) -> Dict:
    """
    Find and rank buyers for a farmer's produce lot.
    """

    # --------------------------------------------------
    # Validate farmer lot input
    # --------------------------------------------------

    if not commodity or not commodity.strip():
        raise ValueError(
            "commodity cannot be empty."
        )

    if quantity <= 0:
        raise ValueError(
            "quantity must be greater than zero."
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
    # Fetch open buyer requirements
    # --------------------------------------------------

    requirements = get_open_buyer_requirements(
        commodity=commodity,
        variety=variety,
        grade=grade,
        limit=limit,
    )

    # --------------------------------------------------
    # Normalize database records
    # --------------------------------------------------

    buyers: List[Dict] = []

    for requirement in requirements:
        buyer = _normalize_buyer_requirement(
            requirement
        )

        if buyer is not None:
            buyers.append(buyer)

    # --------------------------------------------------
    # Farmer lot
    # --------------------------------------------------

    farmer_lot = {
        "farmer_id": "request",
        "lot_id": "request",
        "commodity": commodity,
        "quantity": quantity,
        "variety": variety,
        "grade": grade,
        "location": location,
        "expected_price": expected_price,
    }

    # --------------------------------------------------
    # No usable buyers
    # --------------------------------------------------

    if not buyers:
        return {
            "farmer_lot": farmer_lot,
            "best_buyer": None,
            "matches": [],
        }

    # --------------------------------------------------
    # Run existing matching engine
    # --------------------------------------------------

    result = match_buyers(
        farmer_lot=farmer_lot,
        buyers=buyers,
    )

    return result