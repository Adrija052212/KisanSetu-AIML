import joblib
import pandas as pd
from pathlib import Path

from src.schemas import PriceForecast
from src.forecasting.dataset import (
    create_calendar_features,
    create_series_ids,
    create_calendar_lag_features,
    create_rolling_features,
    create_price_change_features,
)

MODEL_PATH = Path(
    "models/price_forecasting/"
    "global_xgboost_reduced.joblib"
)

MODEL_VERSION = "global_xgboost_reduced_v1"

SERIES_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
]


def load_price_model(model_path=MODEL_PATH):
    """Load the trained global XGBoost forecasting model."""
    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}"
        )

    return joblib.load(model_path)


def prepare_prediction_features(
    historical_data: pd.DataFrame,
    arrival_quantity=None,
):
    """
    Prepare the feature row required for a next-day prediction.

    historical_data must contain observations for one market series,
    sorted or sortable by Date.
    """

    required_columns = SERIES_COLUMNS + [
        "Date",
        "Modal_Price",
        "Arrival_Quantity",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in historical_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = historical_data.copy()

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["Date", "Modal_Price"]
    )

    if data.empty:
        raise ValueError(
            "No valid historical observations available."
        )

    data = data.sort_values("Date").reset_index(drop=True)

    latest_row = data.iloc[-1]

    # The model predicts the next calendar day.
    forecast_date = latest_row["Date"] + pd.Timedelta(days=1)

    # Create a synthetic row representing the date we want to predict.
    prediction_row = latest_row.copy()
    prediction_row["Date"] = forecast_date

    if arrival_quantity is not None:
        prediction_row["Arrival_Quantity"] = arrival_quantity
    else:
        prediction_row["Arrival_Quantity"] = latest_row[
            "Arrival_Quantity"
        ]

    # Current price for the prediction is the latest known price.
    prediction_row["Modal_Price"] = latest_row["Modal_Price"]

    data = pd.concat(
        [
            data,
            pd.DataFrame([prediction_row])
        ],
        ignore_index=True
    )

    data = data.sort_values("Date").reset_index(drop=True)

    # Build the same features used during training.
    data = create_series_ids(
        data,
        SERIES_COLUMNS
    )

    data["current_price"] = data["Modal_Price"]

    data = create_calendar_features(
        data,
        "Date"
    )

    data = create_calendar_lag_features(
        data,
        price_column="Modal_Price",
        date_column="Date",
        group_columns=SERIES_COLUMNS,
        lags=[1, 3, 7, 14, 30]
    )

    data = create_rolling_features(
        data,
        price_column="Modal_Price",
        group_columns=SERIES_COLUMNS
    )

    data = create_price_change_features(
        data,
        price_column="Modal_Price"
    )

    prediction_row = data.iloc[[-1]].copy()

    numeric_features = [
        "current_price",
        "lag_1",
        "lag_3",
        "lag_7",
        "lag_14",
        "lag_30",
        "rolling_mean_7",
        "rolling_std_7",
        "rolling_mean_14",
        "rolling_std_14",
        "rolling_mean_30",
        "rolling_std_30",
        "price_change_1",
        "price_change_7",
        "price_change_30",
        "Arrival_Quantity",
        "day_of_week",
        "day_of_month",
        "month",
        "quarter",
        "day_of_year",
        "week_of_year",
    ]

    categorical_features = [
        "Commodity"
    ]

    feature_columns = (
        numeric_features +
        categorical_features
    )

    X = prediction_row[feature_columns]

    return X, prediction_row


def predict_price(
    historical_data: pd.DataFrame,
    model=None,
    arrival_quantity=None,
):
    """
    Predict the next-day modal price for a market series.
    """

    if model is None:
        model = load_price_model()

    X, prediction_row = prepare_prediction_features(
        historical_data,
        arrival_quantity=arrival_quantity,
    )

    predicted_price = float(
        model.predict(X)[0]
    )

    latest_row = historical_data.sort_values(
        "Date"
    ).iloc[-1]

    series_id = "||".join(
        str(latest_row[column])
        if pd.notna(latest_row[column])
        else "Unknown"
        for column in SERIES_COLUMNS
    )

    result = PriceForecast(
        series_id=series_id,
        commodity=str(latest_row["Commodity"]),
        variety=(
            str(latest_row["Variety"])
            if pd.notna(latest_row["Variety"])
            else None
        ),
        grade=(
            str(latest_row["Grade"])
            if pd.notna(latest_row["Grade"])
            else "Unknown"
        ),
        market=str(latest_row["Market"]),
        forecast_date=prediction_row.iloc[0]["Date"].date(),
        predicted_price=max(0.0, predicted_price),
        model_version=MODEL_VERSION,
    )

    return result