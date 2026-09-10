from src.llm.claude_agent import ClaudeAgent


def test_claude_agent_connection():
    agent = ClaudeAgent()

    response = agent.ask(
        "Say hello to the KisanSetu AI project in one sentence."
    )

    assert response
    assert isinstance(response, str)