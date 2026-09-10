from typing import Dict, List


def recommend_best_time(
    predictions: List[Dict],
    mode: str = "sell"
) -> Dict:
    """
    Recommend the best future time to buy or sell.

    Parameters
    ----------
    predictions : List[Dict]
        Future price predictions.
        Each item must contain:
            - date
            - predicted_price

    mode : str
        "sell" -> choose the highest predicted price.
        "buy"  -> choose the lowest predicted price.

    Returns
    -------
    Dict
        Best timing recommendation and ranked predictions.
    """

    # Validate mode
    mode = str(mode).strip().lower()

    if mode not in {"buy", "sell"}:
        raise ValueError(
            "mode must be either 'buy' or 'sell'."
        )

    # Validate predictions
    if not predictions:
        raise ValueError(
            "predictions cannot be empty."
        )

    required_fields = {
        "date",
        "predicted_price"
    }

    for prediction in predictions:
        missing_fields = (
            required_fields - prediction.keys()
        )

        if missing_fields:
            raise ValueError(
                f"Prediction is missing required "
                f"fields: {sorted(missing_fields)}"
            )

        predicted_price = float(
            prediction["predicted_price"]
        )

        if predicted_price < 0:
            raise ValueError(
                "predicted_price cannot be negative."
            )

    # Create clean prediction records
    cleaned_predictions = []

    for prediction in predictions:
        cleaned_predictions.append(
            {
                "date": prediction["date"],
                "predicted_price": round(
                    float(prediction["predicted_price"]),
                    2
                )
            }
        )

    # Sort according to objective
    if mode == "sell":
        ranked_predictions = sorted(
            cleaned_predictions,
            key=lambda x: x["predicted_price"],
            reverse=True
        )
        recommendation = "SELL"

    else:
        ranked_predictions = sorted(
            cleaned_predictions,
            key=lambda x: x["predicted_price"]
        )
        recommendation = "BUY"

    # Assign ranking
    for rank, prediction in enumerate(
        ranked_predictions,
        start=1
    ):
        prediction["rank"] = rank

    # Best timing
    best_prediction = ranked_predictions[0]

    return {
        "recommendation": recommendation,
        "best_date": best_prediction["date"],
        "best_predicted_price": best_prediction[
            "predicted_price"
        ],
        "ranked_predictions": ranked_predictions,
    }