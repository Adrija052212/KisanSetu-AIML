import pytest
from unittest.mock import patch

from mcp import Client

from src.mcp.server import mcp
from src.mcp.tools.prices import forecast_price_tool


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
                "state": "West Bengal",
                "district": "Nadia",
                "commodity": "Tomato",
                "quantity": 50,
                "mode": "sell",
            },
        )

        assert result.is_error is False
        assert result.content

        text = result.content[0].text

        assert "best_market" in text
        assert "Ranaghat APMC" in text
        assert "current_price" in text
        assert "current_effective_price" in text
        assert "rank" in text


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
                "commodity": "tomato",
                "quantity": 50,
                "grade": "A",
                "location": "Nadia",
                "variety": "hybrid",
                "expected_price": 2300,
            },
        )

        assert result.is_error is False
        assert result.content

        text = result.content[0].text

        assert "best_buyer" in text
        assert "matches" in text
        assert "match_score" in text


@pytest.mark.anyio
async def test_mcp_best_farmers_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "best_farmers",
            {
                "commodity": "potato",
                "required_quantity": 30,
                "grade": "A",
                "location": "kolkata",
                "offered_price": 3600,
            },
        )

        assert result.is_error is False

        text = result.content[0].text

        assert "100" in text
        assert "Excellent" in text
        assert "potato" in text.lower()


def test_forecast_price_tool():
    result = forecast_price_tool(
        state="West Bengal",
        district="Nadia",
        market="Ranaghat APMC",
        commodity="Tomato",
        variety="Other",
        grade="FAQ",
    )

    assert result
    assert "predicted_price" in result
    assert "forecast_date" in result
    assert result["predicted_price"] > 0

    forecast_date = str(result["forecast_date"])

    assert len(forecast_date) == 10
    assert forecast_date[4] == "-"
    assert forecast_date[7] == "-"


@pytest.mark.anyio
async def test_mcp_server_exposes_all_tools():
    async with Client(mcp) as client:
        result = await client.list_tools()

        tool_names = {
            tool.name
            for tool in result.tools
        }

        expected_tools = {
            "forecast_price",
            "buy_recommendation",
            "sell_recommendation",
            "best_time",
            "net_return",
            "best_buyers",
            "best_farmers",
            "current_price",
            "buy_decision",
            "sell_decision",
            "best_market",
        }

        assert tool_names == expected_tools    