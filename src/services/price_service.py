from typing import Dict, Optional

import pandas as pd

from src.forecasting.predictor import predict_price


def forecast_market_price(
    historical_data: pd.DataFrame,
    arrival_quantity: Optional[float] = None,
) -> Dict:
    """
    Generate a future market price forecast.
    """

    forecast = predict_price(
        historical_data=historical_data,
        arrival_quantity=arrival_quantity,
    )

    return forecast.model_dump()