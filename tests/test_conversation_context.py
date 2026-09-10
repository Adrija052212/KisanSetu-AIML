import pytest

from src.llm.claude_agent import ClaudeAgent


@pytest.mark.anyio
async def test_claude_remembers_conversation_context():

    agent = ClaudeAgent()

    first_response = await agent.ask_with_mcp(
        "My crop is tomato and I am selling it in Nadia."
    )

    assert first_response
    assert isinstance(first_response, str)

    second_response = await agent.ask_with_mcp(
        "What crop and location did I just tell you?"
    )

    assert second_response

    response_lower = second_response.lower()

    assert "tomato" in response_lower
    assert "nadia" in response_lower