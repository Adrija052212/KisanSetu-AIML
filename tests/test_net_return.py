import pytest

from src.recommendations.net_return import calculate_net_return


def test_sell_net_return():
    result = calculate_net_return(
        price=2650,
        quantity=10,
        transport_cost=80,
        storage_cost=50,
        other_costs=20,
        mode="sell",
    )

    assert result["gross_value"] == 26500
    assert result["total_costs"] == 1500
    assert result["net_return"] == 25000


def test_buy_total_cost():
    result = calculate_net_return(
        price=2500,
        quantity=10,
        transport_cost=80,
        storage_cost=50,
        other_costs=20,
        mode="buy",
    )

    assert result["gross_value"] == 25000
    assert result["total_costs"] == 1500
    assert result["net_return"] == 26500


def test_zero_transport_storage_and_other_costs():
    result = calculate_net_return(
        price=2000,
        quantity=5,
        mode="sell",
    )

    assert result["total_costs"] == 0
    assert result["net_return"] == 10000


def test_negative_price_rejected():
    with pytest.raises(ValueError):
        calculate_net_return(
            price=-100,
            quantity=10,
        )


def test_invalid_mode_rejected():
    with pytest.raises(ValueError):
        calculate_net_return(
            price=2000,
            quantity=10,
            mode="invalid",
        )