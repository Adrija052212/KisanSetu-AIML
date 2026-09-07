from src.schemas import (
    BuyerRequirement,
    FarmerLot,
    LogisticsCost,
    MarketPrice,
    PriceForecast,
)


def test_all_schemas_are_importable():
    assert FarmerLot is not None
    assert BuyerRequirement is not None
    assert MarketPrice is not None
    assert PriceForecast is not None
    assert LogisticsCost is not None