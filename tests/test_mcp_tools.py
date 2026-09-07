import pytest

from mcp import Client
from src.mcp.server import mcp


@pytest.mark.anyio
async def test_mcp_sell_recommendation_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "sell_recommendation",
            {
                "current_price": 2000,
                "predicted_price": 2200,
                "transport_cost": 100,
                "quantity": 10,
            },
        )

        assert result.is_error is False
        assert result.content

        text = result.content[0].text

        assert "WAIT" in text
        assert "2200" in text


@pytest.mark.anyio
async def test_mcp_best_market_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "best_market",
            {
                "markets": [
                    {
                        "market": "Market A",
                        "current_price": 2500,
                        "transport_cost": 100,
                    },
                    {
                        "market": "Market B",
                        "current_price": 2650,
                        "transport_cost": 80,
                    },
                    {
                        "market": "Market C",
                        "current_price": 2700,
                        "transport_cost": 250,
                    },
                ],
                "quantity": 10,
                "mode": "sell",
            },
        )

        assert result.is_error is False
        assert result.content

        text = result.content[0].text

        assert "Market B" in text


@pytest.mark.anyio
async def test_mcp_best_time_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "best_time",
            {
                "predictions": [
                    {
                        "date": "2026-09-06",
                        "predicted_price": 2400,
                    },
                    {
                        "date": "2026-09-07",
                        "predicted_price": 2460,
                    },
                    {
                        "date": "2026-09-08",
                        "predicted_price": 2510,
                    },
                ],
                "mode": "sell",
            },
        )

        assert result.is_error is False
        assert result.content

        text = result.content[0].text

        assert "2026-09-08" in text
        assert "2510" in text


@pytest.mark.anyio
async def test_mcp_net_return_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "net_return",
            {
                "price": 2500,
                "quantity": 10,
                "transport_cost": 100,
                "storage_cost": 50,
                "other_costs": 20,
                "mode": "sell",
            },
        )

        assert result.is_error is False
        assert result.content

        text = result.content[0].text

        assert "net_return" in text
        assert "23300" in text


@pytest.mark.anyio
async def test_mcp_best_buyers_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "best_buyers",
            {
                "farmer_lot": {
                    "farmer_id": "F001",
                    "lot_id": "L001",
                    "commodity": "Tomato",
                    "quantity": 50,
                    "quantity_unit": "Quintal",
                    "grade": "A",
                    "location": "Nadia",
                    "expected_price": 2200,
                    "available_date": "2026-09-06",
                },
                "buyers": [
                    {
                        "buyer_id": "B001",
                        "requirement_id": "R001",
                        "commodity": "Tomato",
                        "required_quantity": 40,
                        "quantity_unit": "Quintal",
                        "grade": "A",
                        "location": "Nadia",
                        "offered_price": 2300,
                        "required_by_date": "2026-09-08",
                    },
                    {
                        "buyer_id": "B002",
                        "requirement_id": "R002",
                        "commodity": "Tomato",
                        "required_quantity": 60,
                        "quantity_unit": "Quintal",
                        "grade": "Any",
                        "location": "Kolkata",
                        "offered_price": 2400,
                        "required_by_date": "2026-09-08",
                    },
                ],
            },
        )

        assert result.is_error is False
        assert result.content

        text = result.content[0].text

        assert "B001" in text
        assert "match_score" in text


@pytest.mark.anyio
async def test_mcp_best_farmers_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "best_farmers",
            {
                "buyer_requirement": {
                    "buyer_id": "B001",
                    "requirement_id": "R001",
                    "commodity": "Tomato",
                    "required_quantity": 50,
                    "quantity_unit": "Quintal",
                    "grade": "A",
                    "location": "Nadia",
                    "offered_price": 2300,
                    "required_by_date": "2026-09-08",
                },
                "farmers": [
                    {
                        "farmer_id": "F001",
                        "lot_id": "L001",
                        "commodity": "Tomato",
                        "quantity": 50,
                        "quantity_unit": "Quintal",
                        "grade": "A",
                        "location": "Nadia",
                        "expected_price": 2200,
                        "available_date": "2026-09-06",
                    },
                    {
                        "farmer_id": "F002",
                        "lot_id": "L002",
                        "commodity": "Tomato",
                        "quantity": 30,
                        "quantity_unit": "Quintal",
                        "grade": "A",
                        "location": "Kolkata",
                        "expected_price": 2200,
                        "available_date": "2026-09-06",
                    },
                ],
            },
        )

        assert result.is_error is False
        assert result.content

        text = result.content[0].text

        assert "F001" in text
        assert "match_score" in text