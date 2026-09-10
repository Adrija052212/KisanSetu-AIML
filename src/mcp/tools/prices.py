from typing import Any, Dict
from datetime import date, timedelta

from src.data_access.agmarknet_data import (
    get_current_market_price_by_name,
)

from src.data_access.forecast_data import (
    forecast_from_market_records,
)

from src.data_access.market_data import (
    get_market_price_history,
    get_available_market_series,
)

def forecast_price_tool(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str = None,
    grade: str = None,
) -> Dict[str, Any]:
    """
    Forecast the next-day modal price for a market series.

    First tries the exact variety/grade requested by the user.
    If that historical series does not exist, it falls back to
    an available historical series for the same market and commodity.
    """

    # ---------------------------------------------------------
    # 1. Try the exact requested series
    # ---------------------------------------------------------

    historical_records = []

    if variety and variety.strip() and grade and grade.strip():
        historical_records = get_market_price_history(
            state=state,
            district=district,
            market=market,
            commodity=commodity,
            variety=variety,
            grade=grade,
        )

    # ---------------------------------------------------------
    # 2. If exact series is unavailable, find an available one
    # ---------------------------------------------------------

    used_variety = variety
    used_grade = grade
    fallback_used = False

    if not historical_records:

        available_series = get_available_market_series(
            state=state,
            district=district,
            market=market,
            commodity=commodity,
        )

        if not available_series:
            raise ValueError(
                "No historical market data found for the "
                "requested commodity and market."
            )

        selected_series = available_series[0]

        used_variety = selected_series["variety"]
        used_grade = selected_series["grade"]
        fallback_used = True

        historical_records = get_market_price_history(
            state=state,
            district=district,
            market=market,
            commodity=commodity,
            variety=used_variety,
            grade=used_grade,
        )

    if not historical_records:
        raise ValueError(
            "No historical market data found for the "
            "available forecasting series."
        )

    # ---------------------------------------------------------
    # 3. Get latest live price from Agmarknet
    # ---------------------------------------------------------

    live_record = None
    search_date = date.today()

    for _ in range(7):
        try:
            live_record = get_current_market_price_by_name(
                date=search_date.isoformat(),
                state=state,
                district=district,
                market=market,
                commodity=commodity,
                variety=used_variety,
                grade=used_grade,
            )
            break
        except ValueError:
            search_date -= timedelta(days=1)

    if live_record is None:
        raise ValueError(
            "No recent current market price found on Agmarknet "
            "for the requested market and commodity."
        )

    # ---------------------------------------------------------
    # 4. Add live observation to historical records
    # ---------------------------------------------------------

    historical_records = [
        record
        for record in historical_records
        if str(record.get("Date")) != str(
            live_record.get("Date")
        )
    ]

    historical_records.append(live_record)

    # ---------------------------------------------------------
    # 5. Generate forecast using existing XGBoost pipeline
    # ---------------------------------------------------------

    forecast = forecast_from_market_records(
        historical_records
    )

    # ---------------------------------------------------------
    # 6. Add series information for Claude
    # ---------------------------------------------------------

    forecast["requested_variety"] = variety
    forecast["requested_grade"] = grade
    forecast["used_variety"] = used_variety
    forecast["used_grade"] = used_grade
    forecast["fallback_used"] = fallback_used

    return forecast

def current_price_tool(
    date: str,
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str = None,
    grade: str = None,
) -> Dict[str, Any]:
    """
    Get the current mandi price for a specific market and commodity
    from Agmarknet using human-readable names.
    """

    return get_current_market_price_by_name(
        date=date,
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )