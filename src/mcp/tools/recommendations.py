from typing import Any, Dict, List

from src.services.recommendation_service import (
    get_buy_decision,
    get_sell_decision,
    get_best_market,
    get_best_time,
    get_net_return,
)


def buy_recommendation_tool(
    current_price: float,
    predicted_price: float,
    quantity: float = 1.0,
    min_change_percent: float = 2.0,
) -> Dict[str, Any]:
    """
    Recommend whether buying now is favorable.
    """
    return get_buy_decision(
        current_price=current_price,
        predicted_price=predicted_price,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )


def sell_recommendation_tool(
    current_price: float,
    predicted_price: float,
    transport_cost: float = 0.0,
    quantity: float = 1.0,
    min_change_percent: float = 0.0,
) -> Dict[str, Any]:
    """
    Recommend whether to sell now or wait.
    """
    return get_sell_decision(
        current_price=current_price,
        predicted_price=predicted_price,
        transport_cost=transport_cost,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )


def best_market_tool(
    markets: List[Dict[str, Any]],
    quantity: float = 1.0,
    mode: str = "sell",
) -> Dict[str, Any]:
    """
    Find the best market for buying or selling.
    """
    return get_best_market(
        markets=markets,
        quantity=quantity,
        mode=mode,
    )


def best_time_tool(
    predictions: List[Dict[str, Any]],
    mode: str = "sell",
) -> Dict[str, Any]:
    """
    Find the best future time to buy or sell.
    """
    return get_best_time(
        predictions=predictions,
        mode=mode,
    )


def net_return_tool(
    price: float,
    quantity: float,
    transport_cost: float = 0.0,
    storage_cost: float = 0.0,
    other_costs: float = 0.0,
    mode: str = "sell",
) -> Dict[str, Any]:
    """
    Calculate net return after costs.
    """
    return get_net_return(
        price=price,
        quantity=quantity,
        transport_cost=transport_cost,
        storage_cost=storage_cost,
        other_costs=other_costs,
        mode=mode,
    )

