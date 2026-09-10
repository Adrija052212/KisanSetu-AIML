import numpy as np
import pandas as pd


def calculate_metrics(
    actual,
    predicted,
    current_price=None
):
    """
    Calculate forecasting metrics.

    Metrics:
    - MAE
    - RMSE
    - MAPE
    - Directional Accuracy
    """

    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    errors = actual - predicted

    mae = np.mean(np.abs(errors))

    rmse = np.sqrt(
        np.mean(errors ** 2)
    )

    # Avoid division by zero in MAPE.
    non_zero = actual != 0

    if np.any(non_zero):
        mape = np.mean(
            np.abs(
                (actual[non_zero] - predicted[non_zero])
                / actual[non_zero]
            )
        ) * 100
    else:
        mape = np.nan

    directional_accuracy = np.nan

    if current_price is not None:

        current_price = np.asarray(
            current_price,
            dtype=float
        )

        actual_direction = np.sign(
            actual - current_price
        )

        predicted_direction = np.sign(
            predicted - current_price
        )

        directional_accuracy = (
            np.mean(
                actual_direction
                == predicted_direction
            )
            * 100
        )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape,
        "Directional_Accuracy": directional_accuracy
    }


def evaluate_naive_baseline(
    df,
    price_column="Modal_Price",
    target_column="target_1d"
):
    """
    Naive persistence baseline:

        Tomorrow's price = today's price
    """

    data = df.copy()

    required_columns = [
        price_column,
        target_column
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = data[
        data[price_column].notna()
        & data[target_column].notna()
    ].copy()

    actual = data[target_column]
    predicted = data[price_column]
    current_price = data[price_column]

    metrics = calculate_metrics(
        actual,
        predicted,
        current_price
    )

    return metrics


def print_metrics(name, metrics):

    print(f"\n{name}")
    print("-" * 50)

    print(
        f"MAE:                  "
        f"₹{metrics['MAE']:.2f}"
    )

    print(
        f"RMSE:                 "
        f"₹{metrics['RMSE']:.2f}"
    )

    print(
        f"MAPE:                 "
        f"{metrics['MAPE']:.2f}%"
    )

    print(
        f"Directional Accuracy: "
        f"{metrics['Directional_Accuracy']:.2f}%"
    )