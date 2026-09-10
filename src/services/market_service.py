from typing import Dict, List

from src.data_access.market_data import get_market_prices
from src.recommendations.market_recommendation import (
    recommend_best_market,
)


def get_market_recommendation(
    commodity: str,
    quantity: float = 1.0,
    mode: str = "sell",
    state: str = None,
    district: str = None,
    transport_costs: Dict[str, float] = None,
    variety: str = None,
    grade: str = None,
    limit: int = 100,
) -> Dict:
    """
    Fetch current market prices and recommend
    the best market for buying or selling.

    Transport costs are supplied separately because
    current market-price data does not contain them.
    """

    if not commodity or not commodity.strip():
        raise ValueError(
            "commodity cannot be empty."
        )

    if quantity <= 0:
        raise ValueError(
            "quantity must be greater than zero."
        )

    if mode not in {"sell", "buy"}:
        raise ValueError(
            "mode must be either 'sell' or 'buy'."
        )

    if transport_costs is None:
        transport_costs = {}

    # --------------------------------------------------------
    # Fetch current market prices
    # --------------------------------------------------------

    records = get_market_prices(
        commodity=commodity,
        state=state,
        district=district,
        variety=variety,
        grade=grade,
        limit=limit,
    )

    if not records:
        raise ValueError(
            "No current market prices found "
            "for the requested commodity."
        )

    # --------------------------------------------------------
    # Convert market records into recommendation input
    # --------------------------------------------------------

    markets: List[Dict] = []

    for record in records:

        market_name = record.get("Market")
        current_price = record.get("Modal_Price")

        if not market_name:
            continue

        if current_price is None:
            continue

        transport_cost = transport_costs.get(
            market_name,
            0.0,
        )

        markets.append(
            {
                "market": market_name,
                "current_price": float(
                    current_price
                ),
                "transport_cost": float(
                    transport_cost
                ),
            }
        )

    if not markets:
        raise ValueError(
            "No valid market price records found."
        )

    # --------------------------------------------------------
    # Apply market recommendation logic
    # --------------------------------------------------------

    recommendation = recommend_best_market(
        markets=markets,
        quantity=quantity,
        mode=mode,
    )

    return {
        "commodity": commodity,
        "state": state,
        "district": district,
        "variety": variety,
        "grade": grade,
        **recommendation,
    }