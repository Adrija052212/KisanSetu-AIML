from datetime import date as DateType

from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat


class PriceForecast(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    series_id: str = Field(..., min_length=1)

    commodity: str = Field(..., min_length=1)
    variety: str | None = None
    grade: str = "Unknown"
    market: str = Field(..., min_length=1)

    forecast_date: DateType
    predicted_price: NonNegativeFloat

    model_version: str = Field(..., min_length=1)