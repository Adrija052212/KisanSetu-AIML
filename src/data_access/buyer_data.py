from typing import Dict, List, Optional

from src.data_access.supabase_client import get_supabase_client


def get_open_buyer_requirements(
    commodity: Optional[str] = None,
    variety: Optional[str] = None,
    grade: Optional[str] = None,
    limit: int = 100,
) -> List[Dict]:
    """
    Fetch open buyer requirements together with
    the buyer profile information needed by the
    matching engine.
    """

    if limit <= 0:
        raise ValueError(
            "limit must be greater than zero."
        )

    supabase = get_supabase_client()

    query = (
        supabase
        .table("buyer_requirements")
        .select("*")
        .eq("status", "open")
    )

    # Case-insensitive matching.
    if commodity:
        query = query.ilike(
            "crop_name",
            commodity.strip()
        )

    if variety:
        query = query.ilike(
            "variety",
            variety.strip()
        )

    if grade:
        query = query.ilike(
            "grade",
            grade.strip()
        )

    response = query.limit(limit).execute()

    requirements = response.data or []

    if not requirements:
        return []

    buyer_ids = list({
        requirement["buyer_id"]
        for requirement in requirements
        if requirement.get("buyer_id")
    })

    if not buyer_ids:
        return requirements

    profile_response = (
        supabase
        .table("buyer_profiles")
        .select("*")
        .in_("id", buyer_ids)
        .execute()
    )

    profiles = profile_response.data or []

    profile_map = {
        profile["id"]: profile
        for profile in profiles
    }

    for requirement in requirements:
        buyer_id = requirement.get("buyer_id")

        requirement["buyer_profile"] = (
            profile_map.get(buyer_id)
        )

    return requirements