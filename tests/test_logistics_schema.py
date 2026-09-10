import pytest

from src.schemas.logistics import LogisticsCost


def test_valid_logistics_cost():
    logistics = LogisticsCost(
        origin="Nashik",
        destination="Mumbai",
        distance_km=165,
        transport_cost=4500,
        storage_cost=0,
        estimated_delivery_days=1,
    )

    assert logistics.origin == "Nashik"
    assert logistics.destination == "Mumbai"
    assert logistics.distance_km == 165
    assert logistics.transport_cost == 4500
    assert logistics.storage_cost == 0


def test_negative_distance_is_invalid():
    with pytest.raises(ValueError):
        LogisticsCost(
            origin="Nashik",
            destination="Mumbai",
            distance_km=-10,
            transport_cost=4500,
            estimated_delivery_days=1,
        )


def test_negative_transport_cost_is_invalid():
    with pytest.raises(ValueError):
        LogisticsCost(
            origin="Nashik",
            destination="Mumbai",
            distance_km=165,
            transport_cost=-500,
            estimated_delivery_days=1,
        )


def test_storage_cost_defaults_to_zero():
    logistics = LogisticsCost(
        origin="Nashik",
        destination="Mumbai",
        distance_km=165,
        transport_cost=4500,
        estimated_delivery_days=1,
    )

    assert logistics.storage_cost == 0.0


def test_delivery_days_cannot_be_negative():
    with pytest.raises(ValueError):
        LogisticsCost(
            origin="Nashik",
            destination="Mumbai",
            distance_km=165,
            transport_cost=4500,
            estimated_delivery_days=-1,
        )