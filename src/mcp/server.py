from mcp.server import MCPServer

from src.mcp.tools.prices import (
    forecast_price_tool,
    current_price_tool,
)

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

from src.services.decision_service import (
    get_sell_decision_from_market,
    get_buy_decision_from_market,
)

from src.services.market_decision_service import (
    get_best_market_from_agmarknet,
)


mcp = MCPServer("KisanSetu AI")


@mcp.tool()
def forecast_price(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str = None,
    grade: str = None,
):
    """Forecast the future market price for a market and commodity."""
    return forecast_price_tool(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )


@mcp.tool()
def buy_recommendation(
    current_price: float,
    predicted_price: float,
    quantity: float = 1.0,
    min_change_percent: float = 2.0,
) -> dict:
    """Recommend whether buying now is favorable."""

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
    """Recommend whether to sell now or wait."""

    return sell_recommendation_tool(
        current_price=current_price,
        predicted_price=predicted_price,
        transport_cost=transport_cost,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )


@mcp.tool()
def best_time(
    predictions: list[dict],
    mode: str = "sell",
) -> dict:
    """Find the best future date to buy or sell."""

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
    """Calculate net return after applicable costs."""

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
    commodity: str,
    quantity: float,
    grade: str,
    location: str,
    variety: str = None,
    expected_price: float = None,
) -> dict:
    """Find and rank suitable buyers."""

    return best_buyers_tool(
        commodity=commodity,
        quantity=quantity,
        grade=grade,
        location=location,
        variety=variety,
        expected_price=expected_price,
    )


@mcp.tool()
def best_farmers(
    commodity: str,
    required_quantity: float,
    grade: str,
    location: str,
    variety: str = None,
    offered_price: float = None,
    limit: int = 100,
) -> dict:
    """Find and rank suitable farmer lots."""

    return best_farmers_tool(
        commodity=commodity,
        required_quantity=required_quantity,
        grade=grade,
        location=location,
        variety=variety,
        offered_price=offered_price,
        limit=limit,
    )


@mcp.tool()
def current_price(
    date: str,
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str = None,
    grade: str = None,
) -> dict:
    """Get the current mandi price from Agmarknet."""

    return current_price_tool(
        date=date,
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )


@mcp.tool()
def buy_decision(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str,
    grade: str,
    quantity: float,
    min_change_percent: float = 2.0,
) -> dict:
    """Decide whether a buyer should buy now or wait."""

    return get_buy_decision_from_market(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
        quantity=quantity,
        min_change_percent=min_change_percent,
    )


@mcp.tool()
def sell_decision(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str,
    grade: str,
    quantity: float,
    transport_cost: float = 0.0,
    min_change_percent: float = 0.0,
) -> dict:
    """Decide whether a farmer should sell now or wait."""

    return get_sell_decision_from_market(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
        quantity=quantity,
        transport_cost=transport_cost,
        min_change_percent=min_change_percent,
    )


@mcp.tool()
def best_market(
    state: str,
    district: str,
    commodity: str,
    quantity: float = 1.0,
    mode: str = "sell",
    transport_costs: dict = None,
) -> dict:
    """Find the best market for buying or selling."""

    return get_best_market_from_agmarknet(
        state=state,
        district=district,
        commodity=commodity,
        quantity=quantity,
        mode=mode,
        transport_costs=transport_costs,
    )


if __name__ == "__main__":
    mcp.run()