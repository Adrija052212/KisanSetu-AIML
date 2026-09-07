from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, NonNegativeFloat, PositiveFloat


class FarmerLot(BaseModel):
    farmer_id: str = Field(..., min_length=1)
    lot_id: str = Field(..., min_length=1)

    commodity: str = Field(..., min_length=1)
    variety: Optional[str] = None

    quantity: PositiveFloat
    quantity_unit: str = "Quintal"

    grade: str = "Unknown"
    location: str = Field(..., min_length=1)

    expected_price: Optional[NonNegativeFloat] = None
    available_date: date