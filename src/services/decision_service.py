from typing import Dict, Any

from src.data_access.agmarknet_data import (
    get_current_market_price_by_name,
)

from src.mcp.tools.prices import (
    forecast_price_tool,
)

from src.recommendations.sell_recommendation import (
    get_sell_recommendation,
)

from src.recommendations.buy_recommendation import (
    get_buy_recommendation,
)

from datetime import date, timedelta


# ============================================================
# SELL DECISION
# ============================================================

def get_sell_decision_from_market(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str,
    grade: str,
    quantity: float,
    transport_cost: float = 0.0,
    min_change_percent: float = 0.0,
) -> Dict[str, Any]:
    """
    Combine live Agmarknet price, next-day forecast,
    and sell recommendation into one decision.
    """

    if quantity <= 0:
        raise ValueError("quantity must be greater than zero.")

    # ---------------------------------------------------------
    # 1. Get current live market price
    # ---------------------------------------------------------

    current_record = None
    search_date = date.today()

    for _ in range(7):
        try:
            current_record = get_current_market_price_by_name(
                date=search_date.isoformat(),
                state=state,
                district=district,
                market=market,
                commodity=commodity,
                variety=variety,
                grade=grade,
            )
            break

        except ValueError:
            search_date -= timedelta(days=1)

    if current_record is None:
        raise ValueError(
            "No recent current market price found on Agmarknet."
        )

    current_price = float(
        current_record["Modal_Price"]
    )

    # ---------------------------------------------------------
    # 2. Get next-day forecast
    # ---------------------------------------------------------

    forecast = forecast_price_tool(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )

    predicted_price = float(
        forecast["predicted_price"]
    )

    # ---------------------------------------------------------
    # 3. Apply sell recommendation logic
    # ---------------------------------------------------------

    recommendation = get_sell_recommendation(
        current_price=current_price,
        predicted_price=predicted_price,
        transport_cost=transport_cost,
        quantity=quantity,
        price_unit=current_record.get(
            "Price_Unit",
            "Rs./Quintal",
        ),
        min_change_percent=min_change_percent,
    )

    # ---------------------------------------------------------
    # 4. Return complete decision
    # ---------------------------------------------------------

    return {
        "commodity": commodity,
        "variety": variety,
        "grade": grade,
        "state": state,
        "district": district,
        "market": market,
        "current_market_date": current_record["Date"],
        "current_price": current_price,
        "forecast_date": forecast["forecast_date"],
        "predicted_price": predicted_price,
        "quantity": quantity,
        "transport_cost": transport_cost,
        **recommendation,
    }


# ============================================================
# BUY DECISION
# ============================================================

def get_buy_decision_from_market(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str,
    grade: str,
    quantity: float,
    min_change_percent: float = 2.0,
) -> Dict[str, Any]:
    """
    Decide whether a buyer should buy now or wait.

    Uses:

    1. Latest available Agmarknet market price
    2. ML next-day price forecast
    3. Existing buy recommendation logic
    """

    if not state or not state.strip():
        raise ValueError("state cannot be empty.")

    if not district or not district.strip():
        raise ValueError("district cannot be empty.")

    if not market or not market.strip():
        raise ValueError("market cannot be empty.")

    if not commodity or not commodity.strip():
        raise ValueError("commodity cannot be empty.")

    if not variety or not variety.strip():
        raise ValueError("variety cannot be empty.")

    if not grade or not grade.strip():
        raise ValueError("grade cannot be empty.")

    if quantity <= 0:
        raise ValueError("quantity must be greater than zero.")

    # ---------------------------------------------------------
    # 1. Get latest available market price
    # ---------------------------------------------------------

    current_record = None
    search_date = date.today()

    for _ in range(7):
        try:
            current_record = get_current_market_price_by_name(
                date=search_date.isoformat(),
                state=state,
                district=district,
                market=market,
                commodity=commodity,
                variety=variety,
                grade=grade,
            )

            if current_record:
                break

        except ValueError:
            pass

        search_date -= timedelta(days=1)

    if not current_record:
        raise ValueError(
            "No current market price found for the requested "
            "market and commodity combination."
        )

    current_price = float(
        current_record["Modal_Price"]
    )

    current_market_date = current_record["Date"]

    price_unit = current_record.get(
        "Price_Unit",
        "Rs./Quintal",
    )

    # ---------------------------------------------------------
    # 2. Get ML next-day price forecast
    # ---------------------------------------------------------

    forecast_result = forecast_price_tool(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )

    predicted_price = float(
        forecast_result["predicted_price"]
    )

    forecast_date = forecast_result["forecast_date"]

    # ---------------------------------------------------------
    # 3. Apply existing buy recommendation logic
    # ---------------------------------------------------------

    recommendation = get_buy_recommendation(
        current_price=current_price,
        predicted_price=predicted_price,
        quantity=quantity,
        min_change_percent=min_change_percent,
        price_unit=price_unit,
    )

    # ---------------------------------------------------------
    # 4. Return complete decision
    # ---------------------------------------------------------

    return {
        "commodity": commodity,
        "variety": variety,
        "grade": grade,
        "state": state,
        "district": district,
        "market": market,
        "quantity": quantity,
        "current_market_date": current_market_date,
        "current_price": current_price,
        "forecast_date": forecast_date,
        "predicted_price": predicted_price,
        **recommendation,
    }