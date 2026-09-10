from typing import Any, Dict, List
from src.forecasting.predictor import predict_price

import pandas as pd


FORECAST_COLUMNS = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
    "Date",
    "Modal_Price",
    "Arrival_Quantity",
]


def market_records_to_dataframe(
    records: List[Dict[str, Any]],
) -> pd.DataFrame:
    """
    Convert normalized market records into the DataFrame
    structure expected by the price forecasting model.
    """

    if not isinstance(records, list):
        raise ValueError("records must be a list.")

    if not records:
        raise ValueError("records cannot be empty.")

    data = pd.DataFrame(records)

    missing_columns = [
        column
        for column in FORECAST_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required forecast columns: {missing_columns}"
        )

    data = data[FORECAST_COLUMNS].copy()

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce",
    )

    data["Modal_Price"] = pd.to_numeric(
        data["Modal_Price"],
        errors="coerce",
    )

    data["Arrival_Quantity"] = pd.to_numeric(
        data["Arrival_Quantity"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["Date", "Modal_Price"]
    )

    data = data.sort_values("Date").reset_index(drop=True)

    return data

def forecast_from_market_records(
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Convert market records into the forecasting DataFrame
    and generate a price forecast.
    """

    data = market_records_to_dataframe(records)

    forecast = predict_price(
        historical_data=data,
    )

    return forecast.model_dump()    