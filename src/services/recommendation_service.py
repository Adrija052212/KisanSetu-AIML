from typing import Dict, List, Optional

from src.recommendations.buy_recommendation import (
    get_buy_recommendation,
)
from src.recommendations.sell_recommendation import (
    get_sell_recommendation,
)
from src.recommendations.market_recommendation import (
    recommend_best_market,
)
from src.recommendations.timing import (
    recommend_best_time,
)
from src.recommendations.net_return import (
    calculate_net_return,
)
from src.data_access.market_data import get_market_price_history
from src.services.price_service import forecast_market_series

def get_buy_decision(
    current_price: float,
    predicted_price: float,
    quantity: float = 1.0,
    min_change_percent: float = 2.0,
) -> Dict:
    """
    Generate a buy recommendation.
    """

    return get_buy_recommendation(
        current_price=current_price,
        predicted_price=predicted_price,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )


def get_sell_decision(
    current_price: float,
    predicted_price: float,
    transport_cost: float = 0.0,
    quantity: float = 1.0,
    min_change_percent: float = 0.0,
) -> Dict:
    """
    Generate a sell recommendation.
    """

    return get_sell_recommendation(
        current_price=current_price,
        predicted_price=predicted_price,
        transport_cost=transport_cost,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )


def get_best_market(
    markets: List[Dict],
    quantity: float = 1.0,
    mode: str = "sell",
) -> Dict:
    """
    Find the best market for buying or selling.
    """

    return recommend_best_market(
        markets=markets,
        quantity=quantity,
        mode=mode,
    )


def get_best_time(
    predictions: List[Dict],
    mode: str = "sell",
) -> Dict:
    """
    Find the best future time to buy or sell.
    """

    return recommend_best_time(
        predictions=predictions,
        mode=mode,
    )


def get_net_return(
    price: float,
    quantity: float,
    transport_cost: float = 0.0,
    storage_cost: float = 0.0,
    other_costs: float = 0.0,
    mode: str = "sell",
) -> Dict:
    """
    Calculate expected net return or purchase cost.
    """

    return calculate_net_return(
        price=price,
        quantity=quantity,
        transport_cost=transport_cost,
        storage_cost=storage_cost,
        other_costs=other_costs,
        mode=mode,
    )

def get_sell_decision_from_market(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str,
    grade: str,
    quantity: float = 1.0,
    transport_cost: float = 0.0,
    min_change_percent: float = 2.0,
) -> Dict:
    """
    Fetch real market history, forecast the next-day price,
    and generate a sell recommendation.
    """

    records = get_market_price_history(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )

    if not records:
        raise ValueError(
            "No historical market data found for the requested series."
        )

    latest_record = records[-1]

    current_price = latest_record.get("Modal_Price")

    if current_price is None:
        raise ValueError(
            "Latest market record does not contain a modal price."
        )

    forecast = forecast_market_series(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )

    predicted_price = float(forecast["predicted_price"])

    recommendation = get_sell_recommendation(
        current_price=float(current_price),
        predicted_price=predicted_price,
        transport_cost=transport_cost,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )

    return {
        "market": {
            "state": state,
            "district": district,
            "market": market,
            "commodity": commodity,
            "variety": variety,
            "grade": grade,
        },
        "latest_market_record": latest_record,
        "forecast": forecast,
        "recommendation": recommendation,
    }


def get_buy_decision_from_market(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str,
    grade: str,
    quantity: float = 1.0,
    min_change_percent: float = 2.0,
) -> Dict:
    """
    Fetch real market history, forecast the next-day price,
    and generate a buy recommendation.
    """

    records = get_market_price_history(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )

    if not records:
        raise ValueError(
            "No historical market data found for the requested series."
        )

    latest_record = records[-1]

    current_price = latest_record.get("Modal_Price")

    if current_price is None:
        raise ValueError(
            "Latest market record does not contain a modal price."
        )

    forecast = forecast_market_series(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )

    predicted_price = float(forecast["predicted_price"])

    recommendation = get_buy_recommendation(
        current_price=float(current_price),
        predicted_price=predicted_price,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )

    return {
        "market": {
            "state": state,
            "district": district,
            "market": market,
            "commodity": commodity,
            "variety": variety,
            "grade": grade,
        },
        "latest_market_record": latest_record,
        "forecast": forecast,
        "recommendation": recommendation,
    }    