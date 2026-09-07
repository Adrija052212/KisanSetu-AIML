from typing import Dict


def get_buy_recommendation(
    current_price: float,
    predicted_price: float,
    quantity: float = 1.0,
    min_change_percent: float = 2.0,
    price_unit: str = "Rs./Quintal",
) -> Dict:
    """
    Generate a buy/ wait recommendation based on the
    current market price and predicted future price.

    Parameters
    ----------
    current_price : float
        Current market price per unit.

    predicted_price : float
        Predicted future market price per unit.

    quantity : float
        Quantity to buy.

    min_change_percent : float
        Minimum expected price increase required
        before recommending BUY.

    price_unit : str
        Unit of the price.

    Returns
    -------
    Dict
        Buy recommendation and supporting calculations.
    """

    # --------------------------------------------------------
    # Input validation
    # --------------------------------------------------------

    if current_price < 0:
        raise ValueError(
            "current_price cannot be negative."
        )

    if predicted_price < 0:
        raise ValueError(
            "predicted_price cannot be negative."
        )

    if quantity <= 0:
        raise ValueError(
            "quantity must be greater than zero."
        )

    if min_change_percent < 0:
        raise ValueError(
            "min_change_percent cannot be negative."
        )

    # --------------------------------------------------------
    # Calculate expected price change
    # --------------------------------------------------------

    expected_change = (
        predicted_price - current_price
    )

    if current_price == 0:
        expected_change_percent = 0.0
    else:
        expected_change_percent = (
            expected_change / current_price
        ) * 100

    # --------------------------------------------------------
    # Calculate purchase cost and expected value
    # --------------------------------------------------------

    current_purchase_cost = (
        current_price * quantity
    )

    predicted_value = (
        predicted_price * quantity
    )

    expected_gain = (
        predicted_value - current_purchase_cost
    )

    # --------------------------------------------------------
    # Generate recommendation
    # --------------------------------------------------------

    if expected_change_percent >= min_change_percent:

        recommendation = "BUY"

        reason = (
            f"Expected price is higher by "
            f"{expected_change_percent:.2f}%. "
            "Buying now is expected to be favorable."
        )

    elif expected_change_percent < 0:

        recommendation = "WAIT"

        reason = (
            f"Expected price is lower by "
            f"{abs(expected_change_percent):.2f}%. "
            "Waiting is recommended."
        )

    else:

        recommendation = "WAIT"

        reason = (
            f"Expected price increase is only "
            f"{expected_change_percent:.2f}%, which is below "
            f"the {min_change_percent:.2f}% threshold. "
            "Waiting is recommended."
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "recommendation": recommendation,
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "expected_change": round(expected_change, 2),
        "expected_change_percent": round(
            expected_change_percent,
            2,
        ),
        "quantity": quantity,
        "current_purchase_cost": round(
            current_purchase_cost,
            2,
        ),
        "predicted_value": round(
            predicted_value,
            2,
        ),
        "expected_gain": round(
            expected_gain,
            2,
        ),
        "min_change_percent": min_change_percent,
        "price_unit": price_unit,
        "reason": reason,
    }