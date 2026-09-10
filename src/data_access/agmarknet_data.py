from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# AGMARKNET CONFIGURATION
# ============================================================

AGMARKNET_BASE_URL = (
    "https://api.agmarknet.gov.in/v1"
)

DAILY_REPORT_URL = (
    f"{AGMARKNET_BASE_URL}"
    "/prices-and-arrivals/market-report/daily"
)

FILTERS_URL = (
    f"{AGMARKNET_BASE_URL}"
    "/daily-price-arrival/filters"
)


# ============================================================
# REQUEST HEADERS
# ============================================================

AGMARKNET_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://agmarknet.gov.in",
    "Referer": "https://agmarknet.gov.in/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
}


# ============================================================
# HELPERS
# ============================================================

def _to_float(value: Any) -> Optional[float]:
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


# ============================================================
# FETCH DAILY MARKET REPORT
# ============================================================

def _fetch_daily_market_report(
    date: str,
    market_id: int,
    state_id: int,
) -> Dict[str, Any]:

    payload = {
        "date": date,
        "marketIds": [market_id],
        "stateIds": [state_id],
        "includeExcel": False,
    }

    response = requests.post(
        DAILY_REPORT_URL,
        headers=AGMARKNET_HEADERS,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if not isinstance(result, dict):
        raise ValueError(
            "Unexpected response format from Agmarknet."
        )

    if not result.get("success"):
        raise ValueError(
            result.get(
                "message",
                "Agmarknet request failed.",
            )
        )

    return result


# ============================================================
# NORMALIZE DAILY REPORT
# ============================================================

def _normalize_daily_report(
    response: Dict[str, Any],
    date: str,
    district: Optional[str] = None,
) -> List[Dict[str, Any]]:
    normalized_records = []

    states = response.get("states", [])

    if not isinstance(states, list):
        raise ValueError(
            "Unexpected states format from Agmarknet."
        )

    for state in states:

        markets = state.get("markets", [])

        if not isinstance(markets, list):
            continue

        for market in markets:

            market_name = market.get("marketName")

            commodities = market.get(
                "commodities",
                [],
            )

            if not isinstance(commodities, list):
                continue

            for commodity in commodities:

                commodity_name = commodity.get(
                    "commodityName"
                )

                records = commodity.get(
                    "data",
                    [],
                )

                if not isinstance(records, list):
                    continue

                for record in records:

                    normalized_records.append({
                        "State": state.get(
                            "stateName"
                        ),
                        "District": district,
                        "Market": market_name,
                        "Commodity": commodity_name,
                        "Variety": record.get(
                            "variety"
                        ),
                        "Grade": record.get(
                            "grade"
                        ),
                        "Min_Price": _to_float(
                            record.get(
                                "minimumPrice"
                            )
                        ),
                        "Max_Price": _to_float(
                            record.get(
                                "maximumPrice"
                            )
                        ),
                        "Modal_Price": _to_float(
                            record.get(
                                "modalPrice"
                            )
                        ),
                        "Price_Unit": record.get(
                            "unitOfPrice"
                        ),
                        "Arrival_Quantity": _to_float(
                            record.get(
                                "arrivals"
                            )
                        ),
                        "Arrival_Unit": record.get(
                            "unitOfArrivals"
                        ),
                        "Date": date,
                    })

    return normalized_records


# ============================================================
# GET CURRENT MARKET PRICES
# ============================================================

def get_agmarknet_markets(
    state: str,
    district: str,
) -> List[Dict[str, Any]]:
    """
    Return all markets available for a state and district.
    """

    response = requests.get(
        FILTERS_URL,
        headers=AGMARKNET_HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    result = response.json()
    filter_data = result.get("data", {})

    states = filter_data.get("state_data", [])
    districts = filter_data.get("district_data", [])
    markets = filter_data.get("market_data", [])

    state_name = state.strip().lower()
    district_name = district.strip().lower()

    state_record = next(
        (
            item
            for item in states
            if str(item.get("state_name", "")).strip().lower()
            == state_name
        ),
        None,
    )

    if not state_record:
        raise ValueError(f"State not found: {state}")

    state_id = state_record["state_id"]

    district_record = next(
        (
            item
            for item in districts
            if str(item.get("district_name", "")).strip().lower()
            == district_name
            and item.get("state_id") == state_id
        ),
        None,
    )

    if not district_record:
        raise ValueError(f"District not found: {district}")

    district_id = district_record["id"]

    result_markets = [
        {
            "market_id": item["id"],
            "market": item["mkt_name"],
            "state_id": state_id,
            "district_id": district_id,
        }
        for item in markets
        if item.get("state_id") == state_id
        and item.get("district_id") == district_id
    ]

    return result_markets


def get_agmarknet_market_ids(
    state: str,
    district: str,
    market: str,
) -> Dict[str, int]:
    """
    Resolve human-readable state, district, and market names
    to their Agmarknet IDs.
    """

    if not state or not state.strip():
        raise ValueError("state cannot be empty.")

    if not district or not district.strip():
        raise ValueError("district cannot be empty.")

    if not market or not market.strip():
        raise ValueError("market cannot be empty.")

    response = requests.get(
        FILTERS_URL,
        headers=AGMARKNET_HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    filter_data = result.get("data", {})

    state_data = filter_data.get("state_data", [])
    district_data = filter_data.get("district_data", [])
    market_data = filter_data.get("market_data", [])

    # ---------------------------------------------------------
    # Find state
    # ---------------------------------------------------------
    state_item = next(
        (
            item
            for item in state_data
            if str(item.get("state_name", "")).strip().lower()
            == state.strip().lower()
        ),
        None,
    )

    if state_item is None:
        raise ValueError(
            f"State '{state}' was not found on Agmarknet."
        )

    state_id = int(state_item["state_id"])

    # ---------------------------------------------------------
    # Find district belonging to selected state
    # ---------------------------------------------------------
    district_item = next(
        (
            item
            for item in district_data
            if str(item.get("district_name", "")).strip().lower()
            == district.strip().lower()
            and item.get("state_id") == state_id
        ),
        None,
    )

    if district_item is None:
        raise ValueError(
            f"District '{district}' was not found "
            f"in state '{state}' on Agmarknet."
        )

    district_id = int(district_item["id"])

    # ---------------------------------------------------------
    # Find market belonging to selected district and state
    # ---------------------------------------------------------
    market_item = next(
        (
            item
            for item in market_data
            if str(item.get("mkt_name", "")).strip().lower()
            == market.strip().lower()
            and item.get("state_id") == state_id
            and item.get("district_id") == district_id
        ),
        None,
    )

    if market_item is None:
        raise ValueError(
            f"Market '{market}' was not found "
            f"in district '{district}', state '{state}' "
            f"on Agmarknet."
        )

    market_id = int(market_item["id"])

    return {
        "state_id": state_id,
        "district_id": district_id,
        "market_id": market_id,
    }

def get_current_market_prices(
    date: str,
    market_id: int,
    state_id: int,
    district: Optional[str] = None,
) -> List[Dict[str, Any]]:

    response = _fetch_daily_market_report(
        date=date,
        market_id=market_id,
        state_id=state_id,
    )

    return _normalize_daily_report(
        response=response,
        date=date,
        district=district,
    )


# ============================================================
# GET EXACT CURRENT MARKET PRICE
# ============================================================

def get_current_market_price(
    date: str,
    state_id: int,
    market_id: int,
    commodity: str,
    variety: Optional[str] = None,
    grade: Optional[str] = None,
    district: Optional[str] = None,
) -> Dict[str, Any]:

    if not commodity or not commodity.strip():
        raise ValueError(
            "commodity cannot be empty."
        )

    records = get_current_market_prices(
        date=date,
        market_id=market_id,
        state_id=state_id,
        district=district,
    )

    commodity = commodity.strip().lower()

    matching_records = [
        record
        for record in records
        if str(
            record.get("Commodity", "")
        ).strip().lower()
        == commodity
    ]

    if variety is not None:
        variety = variety.strip().lower()

        matching_records = [
            record
            for record in matching_records
            if str(
                record.get("Variety", "")
            ).strip().lower()
            == variety
        ]

    if grade is not None:
        grade = grade.strip().lower()

        matching_records = [
            record
            for record in matching_records
            if str(
                record.get("Grade", "")
            ).strip().lower()
            == grade
        ]

    if not matching_records:
        raise ValueError(
            "No matching current market price "
            "found on Agmarknet."
        )

    return matching_records[0]

def get_current_market_price_by_name(
    date: str,
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: Optional[str] = None,
    grade: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get the current mandi price using human-readable
    state, district, market and commodity names.

    Agmarknet location IDs are resolved internally.
    """

    if not date or not date.strip():
        raise ValueError("date cannot be empty.")

    if not state or not state.strip():
        raise ValueError("state cannot be empty.")

    if not district or not district.strip():
        raise ValueError("district cannot be empty.")

    if not market or not market.strip():
        raise ValueError("market cannot be empty.")

    if not commodity or not commodity.strip():
        raise ValueError("commodity cannot be empty.")

    # --------------------------------------------------------
    # Resolve location names to Agmarknet IDs
    # --------------------------------------------------------

    ids = get_agmarknet_market_ids(
        state=state,
        district=district,
        market=market,
    )

    # --------------------------------------------------------
    # Use the existing working ID-based function
    # --------------------------------------------------------

    return get_current_market_price(
        date=date,
        state_id=ids["state_id"],
        market_id=ids["market_id"],
        commodity=commodity,
        variety=variety,
        grade=grade,
        district=district,
    )    


# ============================================================
# GET HISTORICAL MARKET PRICES FOR ML FORECASTING
# ============================================================

from datetime import datetime, timedelta

import pandas as pd


def get_historical_market_prices(
    end_date: str,
    days: int,
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: Optional[str] = None,
    grade: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch historical daily prices for one exact market series.

    The result is formatted for the price forecasting model.
    """

    if days < 1:
        raise ValueError("days must be at least 1.")

    # Resolve human-readable location to Agmarknet IDs.
    ids = get_agmarknet_market_ids(
        state=state,
        district=district,
        market=market,
    )

    end = datetime.strptime(
        end_date,
        "%Y-%m-%d",
    ).date()

    records = []

    for offset in range(days):
        current_date = end - timedelta(days=offset)
        date_string = current_date.isoformat()

        try:
            daily_records = get_current_market_prices(
                date=date_string,
                market_id=ids["market_id"],
                state_id=ids["state_id"],
                district=district,
            )
        except Exception:
            # Some dates may have no available report.
            continue

        for record in daily_records:
            if (
                str(record.get("Commodity", "")).strip().lower()
                != commodity.strip().lower()
            ):
                continue

            if variety is not None:
                record_variety = str(
                    record.get("Variety", "")
                ).strip().lower()

                if record_variety != variety.strip().lower():
                    continue

            if grade is not None:
                record_grade = str(
                    record.get("Grade", "")
                ).strip().lower()

                if record_grade != grade.strip().lower():
                    continue

            if record.get("Modal_Price") is None:
                continue

            records.append(record)

    if not records:
        raise ValueError(
            "No historical market price data found "
            "for the selected market series."
        )

    data = pd.DataFrame(records)

    # Keep only the columns required by predictor.py.
    required_columns = [
        "State",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade",
        "Date",
        "Modal_Price",
        "Arrival_Quantity",
    ]

    for column in required_columns:
        if column not in data.columns:
            data[column] = None

    data = data[required_columns]

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce",
    )

    data["Modal_Price"] = pd.to_numeric(
        data["Modal_Price"],
        errors="coerce",
    )

    data["Arrival_Quantity"] = pd.to_numeric(
        data["Arrival_Quantity"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["Date", "Modal_Price"]
    )

    data = data.sort_values("Date")

    data = data.drop_duplicates(
        subset=[
            "State",
            "District",
            "Market",
            "Commodity",
            "Variety",
            "Grade",
            "Date",
        ]
    )

    return data.reset_index(drop=True)    