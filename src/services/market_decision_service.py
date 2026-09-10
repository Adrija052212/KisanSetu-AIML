from typing import Dict, Any

from datetime import date, timedelta

from src.data_access.agmarknet_data import (
    get_agmarknet_markets,
    get_current_market_prices,
)

from src.recommendations.market_recommendation import (
    recommend_best_market,
)


def get_best_market_from_agmarknet(
    state: str,
    district: str,
    commodity: str,
    quantity: float,
    mode: str = "sell",
    transport_costs: Dict[str, float] = None,
) -> Dict[str, Any]:

    if not state or not state.strip():
        raise ValueError("state cannot be empty.")

    if not district or not district.strip():
        raise ValueError("district cannot be empty.")

    if not commodity or not commodity.strip():
        raise ValueError("commodity cannot be empty.")

    if quantity <= 0:
        raise ValueError("quantity must be greater than zero.")

    if mode not in {"sell", "buy"}:
        raise ValueError("mode must be either 'sell' or 'buy'.")

    if transport_costs is None:
        transport_costs = {}

    # ---------------------------------------------------------
    # 1. Get all markets in the district
    # ---------------------------------------------------------

    markets = get_agmarknet_markets(
        state=state,
        district=district,
    )

    if not markets:
        raise ValueError(
            "No markets found for the requested state and district."
        )

    # ---------------------------------------------------------
    # 2. Find latest available market prices
    # ---------------------------------------------------------

    search_date = date.today()

    priced_markets = []

    for market_info in markets:

        market_name = market_info["market"]
        market_id = market_info["market_id"]
        state_id = market_info["state_id"]

        records = None
        available_date = None

        # Agmarknet may not have today's data yet.
        # Search backwards up to 7 days.

        for _ in range(7):

            try:
                records = get_current_market_prices(
                    date=search_date.isoformat(),
                    market_id=market_id,
                    state_id=state_id,
                    district=district,
                )

                if records:
                    available_date = search_date.isoformat()
                    break

            except Exception:
                pass

            search_date -= timedelta(days=1)

        if not records:
            # Reset search date for the next market.
            search_date = date.today()
            continue

        # -----------------------------------------------------
        # 3. Find requested commodity
        # -----------------------------------------------------

        for record in records:

            record_commodity = str(
                record.get("Commodity", "")
            ).strip().lower()

            if record_commodity != commodity.strip().lower():
                continue

            current_price = record.get("Modal_Price")

            if current_price is None:
                continue

            priced_markets.append({
                "market": market_name,
                "current_price": float(current_price),
                "transport_cost": float(
                    transport_costs.get(
                        market_name,
                        0.0,
                    )
                ),
            })

            break

        # Reset date for next market.
        search_date = date.today()

    # ---------------------------------------------------------
    # 4. Validate results
    # ---------------------------------------------------------

    if not priced_markets:
        raise ValueError(
            "No current prices found for the requested commodity "
            "in the selected district."
        )

    # ---------------------------------------------------------
    # 5. Rank markets
    # ---------------------------------------------------------

    recommendation = recommend_best_market(
        markets=priced_markets,
        quantity=quantity,
        mode=mode,
    )

    return {
        "commodity": commodity,
        "state": state,
        "district": district,
        **recommendation,
    }