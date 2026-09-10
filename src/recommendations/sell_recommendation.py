from typing import Dict


def get_sell_recommendation(
    current_price: float,
    predicted_price: float,
    transport_cost: float = 0.0,
    quantity: float = 1.0,
    price_unit: str = "Rs./Quintal",
    min_change_percent: float = 0.0,
) -> Dict:
    """
    Generate a SELL / WAIT recommendation based on
    current and predicted future prices.

    Parameters
    ----------
    current_price : float
        Current market modal price per unit.

    predicted_price : float
        Predicted future modal price per unit.

    transport_cost : float, optional
        Transport cost per unit.

    quantity : float, optional
        Quantity being sold.

    price_unit : str, optional
        Price unit used by the market data.

    min_change_percent : float, optional
        Minimum expected percentage increase required
        before recommending WAIT.

    Returns
    -------
    Dict
        Structured recommendation result.
    """

    # -----------------------------
    # Validation
    # -----------------------------

    if current_price < 0:
        raise ValueError("current_price cannot be negative.")

    if predicted_price < 0:
        raise ValueError("predicted_price cannot be negative.")

    if transport_cost < 0:
        raise ValueError("transport_cost cannot be negative.")

    if quantity <= 0:
        raise ValueError("quantity must be greater than zero.")

    # -----------------------------
    # Net returns per unit
    # -----------------------------

    current_net_price = current_price - transport_cost
    expected_net_price = predicted_price - transport_cost

    # -----------------------------
    # Expected price movement
    # -----------------------------

    expected_change = predicted_price - current_price

    if current_price == 0:
        expected_change_percent = 0.0
    else:
        expected_change_percent = (
            expected_change / current_price
        ) * 100

    # -----------------------------
    # Total expected returns
    # -----------------------------

    current_total_return = current_net_price * quantity
    expected_total_return = expected_net_price * quantity

    # -----------------------------
    # Decision
    # -----------------------------

    if expected_change_percent > min_change_percent:
        recommendation = "WAIT"

        reason = (
            f"Expected price is higher by "
            f"{expected_change_percent:.2f}%. "
            f"Waiting is expected to provide a better return."
        )

    elif expected_change_percent < 0:
        recommendation = "SELL"

        reason = (
            f"Expected price is lower by "
            f"{abs(expected_change_percent):.2f}%. "
            f"Selling now is expected to provide a better return."
        )

    else:
        recommendation = "SELL"

        reason = (
            f"Expected price increase is only "
            f"{expected_change_percent:.2f}%, which is below "
            f"the {min_change_percent:.2f}% threshold. "
            f"Selling now is recommended."
        )

    # -----------------------------
    # Return structured result
    # -----------------------------

    return {
        "recommendation": recommendation,
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "transport_cost": round(transport_cost, 2),
        "current_net_price": round(current_net_price, 2),
        "expected_net_price": round(expected_net_price, 2),
        "expected_change": round(expected_change, 2),
        "expected_change_percent": round(
            expected_change_percent, 2
        ),
        "quantity": quantity,
        "current_total_return": round(
            current_total_return, 2
        ),
        "expected_total_return": round(
            expected_total_return, 2
        ),
        "price_unit": price_unit,
        "reason": reason,
    }