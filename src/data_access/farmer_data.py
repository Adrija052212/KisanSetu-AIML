from typing import Dict, List, Optional

from src.data_access.supabase_client import get_supabase_client


def get_active_farmer_listings(
    commodity: Optional[str] = None,
    variety: Optional[str] = None,
    grade: Optional[str] = None,
    limit: int = 100,
) -> List[Dict]:
    """
    Fetch active farmer produce listings from Supabase.
    """

    if limit <= 0:
        raise ValueError(
            "limit must be greater than zero."
        )

    supabase = get_supabase_client()

    query = (
        supabase
        .table("produce_listings")
        .select("*")
        .eq("status", "active")
    )

    # Case-insensitive commodity matching.
    if commodity:
        query = query.ilike(
            "crop_name",
            commodity.strip()
        )

    # Variety is optional.
    if variety:
        query = query.ilike(
            "variety",
            variety.strip()
        )

    # Grade is optional.
    if grade:
        query = query.ilike(
            "grade",
            grade.strip()
        )

    response = query.limit(limit).execute()

    return response.data or []