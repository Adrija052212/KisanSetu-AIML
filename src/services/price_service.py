from typing import Dict, Optional

import pandas as pd

from src.data_access.market_data import get_market_price_history
from src.data_access.forecast_data import forecast_from_market_records
from src.forecasting.predictor import predict_price


def forecast_market_price(
    historical_data: pd.DataFrame,
    arrival_quantity: Optional[float] = None,
) -> Dict:
    forecast = predict_price(
        historical_data=historical_data,
        arrival_quantity=arrival_quantity,
    )
    return forecast.model_dump()


def forecast_market_series(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str,
    grade: str,
    arrival_quantity: Optional[float] = None,
) -> Dict:
    """
    Fetch historical market data for one exact market series
    and generate a price forecast.
    """

    records = get_market_price_history(
        state=state,
        district=district,
        market=market,
        commodity=commodity,
        variety=variety,
        grade=grade,
    )

    if not records:
        raise ValueError(
            "No historical market data found for the requested series."
        )

    forecast = forecast_from_market_records(records)

    return forecast