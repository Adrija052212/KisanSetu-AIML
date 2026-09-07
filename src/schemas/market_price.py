from datetime import date as DateType
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat


class MarketPrice(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: DateType = Field(..., alias="Date")

    state: str = Field(..., min_length=1, alias="State")
    district: str = Field(..., min_length=1, alias="District")
    market: str = Field(..., min_length=1, alias="Market")

    commodity_group: Optional[str] = Field(
        None,
        alias="Commodity_Group"
    )
    commodity: str = Field(..., min_length=1, alias="Commodity")
    variety: Optional[str] = Field(None, alias="Variety")
    grade: str = Field("Unknown", alias="Grade")

    min_price: NonNegativeFloat = Field(..., alias="Min_Price")
    max_price: NonNegativeFloat = Field(..., alias="Max_Price")
    modal_price: NonNegativeFloat = Field(..., alias="Modal_Price")

    price_unit: str = Field("Rs./Quintal", alias="Price_Unit")

    arrival_quantity: Optional[NonNegativeFloat] = Field(
        None,
        alias="Arrival_Quantity"
    )
    arrival_unit: Optional[str] = Field(
        None,
        alias="Arrival_Unit"
    )