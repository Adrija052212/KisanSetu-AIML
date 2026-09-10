from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, NonNegativeFloat, PositiveFloat


class BuyerRequirement(BaseModel):
    buyer_id: str = Field(..., min_length=1)
    requirement_id: str = Field(..., min_length=1)

    commodity: str = Field(..., min_length=1)
    variety: Optional[str] = None

    required_quantity: PositiveFloat
    quantity_unit: str = "Quintal"

    grade: str = "Any"
    location: str = Field(..., min_length=1)

    offered_price: NonNegativeFloat
    required_by_date: date