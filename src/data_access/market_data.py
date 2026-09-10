from typing import Any, Dict, List, Optional

import os

import requests
from dotenv import load_dotenv

from src.data_access.supabase_client import get_supabase_client


load_dotenv()


# ============================================================
# DATA.GOV.IN CONFIGURATION
# ============================================================

DATA_GOV_RESOURCE_ID = (
    "9ef84268-d588-465a-a308-a864a43d0070"
)

DATA_GOV_BASE_URL = (
    f"https://api.data.gov.in/resource/"
    f"{DATA_GOV_RESOURCE_ID}"
)


# ============================================================
# DATA.GOV.IN FIELD ALIASES
# ============================================================

FIELD_ALIASES = {
    "State": ["State", "State/UT"],
    "District": ["District"],
    "Market": ["Market"],
    "Commodity_Group": [
        "Commodity Group",
        "Commodity_Group",
    ],
    "Commodity": ["Commodity"],
    "Variety": ["Variety"],
    "Grade": ["Grade"],
    "Min_Price": [
        "Min Price",
        "Min_Price",
    ],
    "Max_Price": [
        "Max Price",
        "Max_Price",
    ],
    "Modal_Price": [
        "Modal Price",
        "Modal_Price",
    ],
    "Price_Unit": [
        "Price Unit",
        "Price_Unit",
    ],
    "Arrival_Quantity": [
        "Arrival Quantity",
        "Arrival_Quantity",
    ],
    "Arrival_Unit": [
        "Arrival Unit",
        "Arrival_Unit",
    ],
    "Date": [
        "Arrival Date",
        "Arrival_Date",
        "Date",
    ],
}


# ============================================================
# DATA.GOV.IN HELPERS
# ============================================================

def _get_field(
    record: Dict[str, Any],
    field: str,
):
    for alias in FIELD_ALIASES[field]:
        if alias in record:
            return record[alias]

    return None


def _to_float(value):
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

        value = value.replace(",", "")

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def normalize_market_record(
    record: Dict[str, Any]
) -> Dict[str, Any]:

    if not isinstance(record, dict):
        raise ValueError(
            "record must be a dictionary."
        )

    return {
        "State": _get_field(
            record,
            "State"
        ),
        "District": _get_field(
            record,
            "District"
        ),
        "Market": _get_field(
            record,
            "Market"
        ),
        "Commodity_Group": _get_field(
            record,
            "Commodity_Group"
        ),
        "Commodity": _get_field(
            record,
            "Commodity"
        ),
        "Variety": _get_field(
            record,
            "Variety"
        ),
        "Grade": _get_field(
            record,
            "Grade"
        ),
        "Min_Price": _to_float(
            _get_field(
                record,
                "Min_Price"
            )
        ),
        "Max_Price": _to_float(
            _get_field(
                record,
                "Max_Price"
            )
        ),
        "Modal_Price": _to_float(
            _get_field(
                record,
                "Modal_Price"
            )
        ),
        "Price_Unit": _get_field(
            record,
            "Price_Unit"
        ),
        "Arrival_Quantity": _to_float(
            _get_field(
                record,
                "Arrival_Quantity"
            )
        ),
        "Arrival_Unit": _get_field(
            record,
            "Arrival_Unit"
        ),
        "Date": _get_field(
            record,
            "Date"
        ),
    }


def normalize_market_records(
    records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if not isinstance(records, list):
        raise ValueError(
            "records must be a list."
        )

    return [
        normalize_market_record(record)
        for record in records
    ]


# ============================================================
# DATA.GOV.IN REQUEST
# ============================================================

def _fetch_market_records(
    filters: Dict[str, Any],
    limit: int = 100,
) -> List[Dict[str, Any]]:

    if limit <= 0:
        raise ValueError(
            "limit must be greater than zero."
        )

    api_key = os.getenv(
        "DATA_GOV_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "DATA_GOV_API_KEY is not set."
        )

    params = {
        "api-key": api_key,
        "format": "json",
        "limit": limit,
    }

    for field, value in filters.items():

        if (
            value is not None
            and str(value).strip()
        ):
            params[
                f"filters[{field}]"
            ] = str(value).strip()

    response = requests.get(
        DATA_GOV_BASE_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    records = payload.get(
        "records",
        []
    )

    if not isinstance(records, list):
        raise ValueError(
            "Unexpected response format "
            "from data.gov.in."
        )

    return records


# ============================================================
# LIVE / CURRENT MARKET PRICES
# ============================================================

def get_market_prices(
    commodity: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    market: Optional[str] = None,
    variety: Optional[str] = None,
    grade: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:

    filters = {
        "commodity": commodity,
        "state": state,
        "district": district,
        "market": market,
        "variety": variety,
        "grade": grade,
    }

    records = _fetch_market_records(
        filters=filters,
        limit=limit,
    )

    return normalize_market_records(
        records
    )


# ============================================================
# SUPABASE HISTORICAL MARKET DATA
# ============================================================

def get_market_price_history(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str,
    grade: str,
    limit: int = 1000,
) -> List[Dict[str, Any]]:

    required_fields = {
        "state": state,
        "district": district,
        "market": market,
        "commodity": commodity,
        "variety": variety,
        "grade": grade,
    }

    for field, value in required_fields.items():

        if (
            value is None
            or not str(value).strip()
        ):
            raise ValueError(
                f"{field} cannot be empty."
            )

    if limit <= 0:
        raise ValueError(
            "limit must be greater than zero."
        )

    # --------------------------------------------------------
    # Connect to Supabase
    # --------------------------------------------------------

    supabase = get_supabase_client()

    all_records = []

    # Supabase returns a limited number of rows
    # per request, so retrieve the series in pages.
    page_size = min(limit, 1000)

    start = 0

    while True:

        end = start + page_size - 1

        response = (
            supabase
            .table("market_price_history")
            .select("*")
            .eq("state", state)
            .eq("district", district)
            .eq("market", market)
            .eq("commodity", commodity)
            .eq("variety", variety)
            .eq("grade", grade)
            .order("date")
            .range(start, end)
            .execute()
        )

        records = response.data or []

        all_records.extend(records)

        # No more records
        if len(records) < page_size:
            break

        # Respect requested limit
        if len(all_records) >= limit:
            all_records = all_records[:limit]
            break

        start += page_size

    # --------------------------------------------------------
    # Convert Supabase field names to the standard
    # forecasting schema
    # --------------------------------------------------------

    normalized = []

    for record in all_records:

        normalized.append({
            "State": record.get("state"),
            "District": record.get("district"),
            "Market": record.get("market"),
            "Commodity_Group": record.get(
                "commodity_group"
            ),
            "Commodity": record.get(
                "commodity"
            ),
            "Variety": record.get(
                "variety"
            ),
            "Grade": record.get(
                "grade"
            ),
            "Min_Price": _to_float(
                record.get("min_price")
            ),
            "Max_Price": _to_float(
                record.get("max_price")
            ),
            "Modal_Price": _to_float(
                record.get("modal_price")
            ),
            "Price_Unit": record.get(
                "price_unit"
            ),
            "Arrival_Quantity": _to_float(
                record.get(
                    "arrival_quantity"
                )
            ),
            "Arrival_Unit": record.get(
                "arrival_unit"
            ),
            "Date": record.get("date"),
        })

    return normalized


def get_available_market_series(
    state: str,
    district: str,
    market: str,
    commodity: str,
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Find available historical variety/grade series for a
    market and commodity.
    """

    if not state or not state.strip():
        raise ValueError("state cannot be empty.")

    if not district or not district.strip():
        raise ValueError("district cannot be empty.")

    if not market or not market.strip():
        raise ValueError("market cannot be empty.")

    if not commodity or not commodity.strip():
        raise ValueError("commodity cannot be empty.")

    if limit <= 0:
        raise ValueError("limit must be greater than zero.")

    supabase = get_supabase_client()

    response = (
        supabase
        .table("market_price_history")
        .select(
            "state,district,market,commodity,variety,grade,date"
        )
        .eq("state", state)
        .eq("district", district)
        .eq("market", market)
        .eq("commodity", commodity)
        .order("date")
        .range(0, limit - 1)
        .execute()
    )

    records = response.data or []

    series = {}

    for record in records:
        variety = record.get("variety")
        grade = record.get("grade")

        if variety is None or grade is None:
            continue

        variety = str(variety).strip()
        grade = str(grade).strip()

        if not variety or not grade:
            continue

        key = (variety.lower(), grade.lower())

        if key not in series:
            series[key] = {
                "variety": variety,
                "grade": grade,
                "record_count": 0,
            }

        series[key]["record_count"] += 1

    return sorted(
        series.values(),
        key=lambda item: item["record_count"],
        reverse=True,
    )    