from typing import Dict, List


def recommend_best_market(
    markets: List[Dict],
    quantity: float = 1.0,
    mode: str = "sell",
) -> Dict:
    """
    Rank markets based on current price and transport cost.

    Parameters
    ----------
    markets : List[Dict]
        List of market information.

        Required fields:
            market
            current_price
            transport_cost

        Optional fields:
            predicted_price

    quantity : float
        Quantity being bought or sold.

    mode : str
        "sell" -> prefer the highest effective selling price.
        "buy"  -> prefer the lowest effective buying cost.

    Returns
    -------
    Dict
        Ranked market recommendations.
    """

    # ========================================================
    # Validation
    # ========================================================

    if not markets:
        raise ValueError("markets cannot be empty.")

    if quantity <= 0:
        raise ValueError(
            "quantity must be greater than zero."
        )

    if mode not in {"sell", "buy"}:
        raise ValueError(
            "mode must be either 'sell' or 'buy'."
        )

    # ========================================================
    # Process each market
    # ========================================================

    results = []

    for market in markets:

        # ----------------------------------------------------
        # Required fields
        # ----------------------------------------------------

        if "market" not in market:
            raise ValueError(
                "Each market must contain a 'market' field."
            )

        if "current_price" not in market:
            raise ValueError(
                "Each market must contain a "
                "'current_price' field."
            )

        if "transport_cost" not in market:
            raise ValueError(
                "Each market must contain a "
                "'transport_cost' field."
            )

        # ----------------------------------------------------
        # Read values
        # ----------------------------------------------------

        market_name = market["market"]

        current_price = float(
            market["current_price"]
        )

        transport_cost = float(
            market["transport_cost"]
        )

        # ----------------------------------------------------
        # Validate values
        # ----------------------------------------------------

        if current_price < 0:
            raise ValueError(
                f"current_price cannot be negative "
                f"for {market_name}."
            )

        if transport_cost < 0:
            raise ValueError(
                f"transport_cost cannot be negative "
                f"for {market_name}."
            )

        # ====================================================
        # Calculate current effective price
        # ====================================================

        if mode == "sell":

            # Farmer sells at the market.
            # Transport cost reduces the actual return.

            current_effective_price = (
                current_price - transport_cost
            )

        else:

            # Buyer purchases from the market.
            # Transport cost increases the actual cost.

            current_effective_price = (
                current_price + transport_cost
            )

        current_total = (
            current_effective_price * quantity
        )

        # ====================================================
        # Predicted price
        # ====================================================

        predicted_price = market.get(
            "predicted_price"
        )

        predicted_effective_price = None
        predicted_total = None

        if predicted_price is not None:

            predicted_price = float(
                predicted_price
            )

            if predicted_price < 0:
                raise ValueError(
                    f"predicted_price cannot be negative "
                    f"for {market_name}."
                )

            if mode == "sell":

                predicted_effective_price = (
                    predicted_price - transport_cost
                )

            else:

                predicted_effective_price = (
                    predicted_price + transport_cost
                )

            predicted_total = (
                predicted_effective_price * quantity
            )

        # ====================================================
        # Expected price change
        # ====================================================

        expected_change = None
        expected_change_percent = None

        if predicted_price is not None:

            expected_change = (
                predicted_price - current_price
            )

            if current_price != 0:

                expected_change_percent = (
                    expected_change / current_price
                ) * 100

        # ====================================================
        # Store market result
        # ====================================================

        results.append(
            {
                "market": market_name,

                "current_price": round(
                    current_price,
                    2,
                ),

                "transport_cost": round(
                    transport_cost,
                    2,
                ),

                "current_effective_price": round(
                    current_effective_price,
                    2,
                ),

                "current_total": round(
                    current_total,
                    2,
                ),

                "predicted_price": (
                    round(
                        predicted_price,
                        2,
                    )
                    if predicted_price is not None
                    else None
                ),

                "predicted_effective_price": (
                    round(
                        predicted_effective_price,
                        2,
                    )
                    if predicted_effective_price is not None
                    else None
                ),

                "predicted_total": (
                    round(
                        predicted_total,
                        2,
                    )
                    if predicted_total is not None
                    else None
                ),

                "expected_change": (
                    round(
                        expected_change,
                        2,
                    )
                    if expected_change is not None
                    else None
                ),

                "expected_change_percent": (
                    round(
                        expected_change_percent,
                        2,
                    )
                    if expected_change_percent is not None
                    else None
                ),
            }
        )

    # ========================================================
    # Rank markets
    # ========================================================

    if mode == "sell":

        # Highest effective selling price is best.

        results.sort(
            key=lambda x: x[
                "current_effective_price"
            ],
            reverse=True,
        )

    else:

        # Lowest effective buying cost is best.

        results.sort(
            key=lambda x: x[
                "current_effective_price"
            ]
        )

    # ========================================================
    # Add ranking
    # ========================================================

    for rank, result in enumerate(
        results,
        start=1,
    ):
        result["rank"] = rank

    # ========================================================
    # Select best market
    # ========================================================

    best_market = results[0]

    if mode == "sell":

        recommendation = (
            f"Sell at {best_market['market']} "
            f"because it provides the highest net "
            f"return after transport cost."
        )

    else:

        recommendation = (
            f"Buy from {best_market['market']} "
            f"because it provides the lowest "
            f"effective purchase cost."
        )

    # ========================================================
    # Final response
    # ========================================================

    return {
        "mode": mode,
        "quantity": quantity,
        "best_market": best_market["market"],
        "recommendation": recommendation,
        "markets": results,
    }