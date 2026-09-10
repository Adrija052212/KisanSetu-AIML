import pytest

from src.llm.claude_agent import ClaudeAgent


@pytest.mark.anyio
async def test_claude_follows_kisensetu_market_scope():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        "What can you help me with in KisanSetu?"
    )

    assert response

    response_lower = response.lower()

    assert "price" in response_lower
    assert "buy" in response_lower or "sell" in response_lower