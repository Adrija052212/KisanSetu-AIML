import pytest
from mcp import Client
from src.mcp.server import mcp


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
            "best_market",
            "best_time",
            "net_return",
            "best_buyers",
            "best_farmers",
            "current_price",
            "buy_decision",
            "sell_decision",
        }

        assert tool_names == expected_tools

@pytest.mark.anyio
async def test_mcp_buy_recommendation_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "buy_recommendation",
            {
                "current_price": 2000,
                "predicted_price": 2100,
                "quantity": 10,
                "min_change_percent": 2.0,
            },
        )

        assert result.is_error is False
        assert result.content

        # MCP returned the tool result as content.
        text = result.content[0].text

        assert "BUY" in text
        assert "2100" in text
        assert "2000" in text

@pytest.mark.anyio
async def test_forecast_price_tool_schema():
    async with Client(mcp) as client:
        tools_result = await client.list_tools()

        forecast_tool = next(
            tool
            for tool in tools_result.tools
            if tool.name == "forecast_price"
        )

        properties = forecast_tool.input_schema["properties"]

        expected_fields = {
            "state",
            "district",
            "market",
            "commodity",
            "variety",
            "grade",
        }

        assert set(properties.keys()) == expected_fields        