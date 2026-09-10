from pydantic import BaseModel, Field, NonNegativeFloat


class LogisticsCost(BaseModel):
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)

    distance_km: NonNegativeFloat
    transport_cost: NonNegativeFloat
    storage_cost: NonNegativeFloat = 0.0

    estimated_delivery_days: NonNegativeFloat