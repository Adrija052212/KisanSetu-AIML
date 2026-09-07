from mcp.server import MCPServer

from src.mcp.tools.prices import forecast_price_tool
from src.mcp.tools.recommendations import (
    buy_recommendation_tool,
    sell_recommendation_tool,
    best_market_tool,
    best_time_tool,
    net_return_tool,
)
from src.mcp.tools.matching import (
    best_buyers_tool,
    best_farmers_tool,
)


mcp = MCPServer("KisanSetu AI")


@mcp.tool()
def forecast_price(
    historical_data: list[dict],
    arrival_quantity: float | None = None,
) -> dict:
    """Forecast the future market price using historical market data."""
    return forecast_price_tool(
        historical_data=historical_data,
        arrival_quantity=arrival_quantity,
    )


@mcp.tool()
def buy_recommendation(
    current_price: float,
    predicted_price: float,
    quantity: float = 1.0,
    min_change_percent: float = 2.0,
) -> dict:
    """Recommend whether buying now is favorable based on current and predicted prices."""
    return buy_recommendation_tool(
        current_price=current_price,
        predicted_price=predicted_price,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )


@mcp.tool()
def sell_recommendation(
    current_price: float,
    predicted_price: float,
    transport_cost: float = 0.0,
    quantity: float = 1.0,
    min_change_percent: float = 0.0,
) -> dict:
    """Recommend whether to sell now or wait based on predicted price and costs."""
    return sell_recommendation_tool(
        current_price=current_price,
        predicted_price=predicted_price,
        transport_cost=transport_cost,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )


@mcp.tool()
def best_market(
    markets: list[dict],
    quantity: float = 1.0,
    mode: str = "sell",
) -> dict:
    """Find the best market for buying or selling after considering transport cost."""
    return best_market_tool(
        markets=markets,
        quantity=quantity,
        mode=mode,
    )


@mcp.tool()
def best_time(
    predictions: list[dict],
    mode: str = "sell",
) -> dict:
    """Find the best future date to buy or sell based on predicted prices."""
    return best_time_tool(
        predictions=predictions,
        mode=mode,
    )


@mcp.tool()
def net_return(
    price: float,
    quantity: float,
    transport_cost: float = 0.0,
    storage_cost: float = 0.0,
    other_costs: float = 0.0,
    mode: str = "sell",
) -> dict:
    """Calculate the net return after transport, storage, and other costs."""
    return net_return_tool(
        price=price,
        quantity=quantity,
        transport_cost=transport_cost,
        storage_cost=storage_cost,
        other_costs=other_costs,
        mode=mode,
    )


@mcp.tool()
def best_buyers(
    farmer_lot: dict,
    buyers: list[dict],
) -> dict:
    """Find and rank the best buyers for a farmer's lot."""
    return best_buyers_tool(
        farmer_lot=farmer_lot,
        buyers=buyers,
    )


@mcp.tool()
def best_farmers(
    buyer_requirement: dict,
    farmers: list[dict],
) -> dict:
    """Find and rank the best farmer lots for a buyer requirement."""
    return best_farmers_tool(
        buyer_requirement=buyer_requirement,
        farmers=farmers,
    )


if __name__ == "__main__":
    mcp.run()

