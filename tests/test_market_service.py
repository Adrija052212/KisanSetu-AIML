from src.services import market_service


def test_get_market_recommendation(monkeypatch):

    fake_records = [
        {
            "Market": "Market A",
            "Modal_Price": 2500.0,
        },
        {
            "Market": "Market B",
            "Modal_Price": 2650.0,
        },
        {
            "Market": "Market C",
            "Modal_Price": 2700.0,
        },
    ]

    def fake_get_market_prices(**kwargs):
        return fake_records

    monkeypatch.setattr(
        market_service,
        "get_market_prices",
        fake_get_market_prices,
    )

    result = market_service.get_market_recommendation(
        commodity="Tomato",
        quantity=10,
        mode="sell",
        transport_costs={
            "Market A": 100,
            "Market B": 80,
            "Market C": 250,
        },
    )

    assert result["best_market"] == "Market B"

    assert (
        result["markets"][0]["current_effective_price"]
        == 2570.0
    )