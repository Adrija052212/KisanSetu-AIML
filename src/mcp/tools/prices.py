from typing import Any, Dict, List, Optional

import pandas as pd

from src.services.price_service import forecast_market_price


def forecast_price_tool(
    historical_data: List[Dict[str, Any]],
    arrival_quantity: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Forecast the future market price using historical market data.

    Parameters
    ----------
    historical_data:
        Historical market price records for one market/commodity series.

    arrival_quantity:
        Optional current arrival quantity in quintals.

    Returns
    -------
    Dict[str, Any]
        Structured price forecast.
    """

    if not historical_data:
        raise ValueError(
            "historical_data cannot be empty."
        )

    data = pd.DataFrame(historical_data)

    forecast = forecast_market_price(
        historical_data=data,
        arrival_quantity=arrival_quantity,
    )

    return forecast