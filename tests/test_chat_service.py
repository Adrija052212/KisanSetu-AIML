import pytest

from src.services.chat_service import ChatService


def test_chat_service_creates_separate_agents():

    service = ChatService()

    agent_a = service.get_agent("conversation_a")
    agent_b = service.get_agent("conversation_b")

    assert agent_a is not agent_b


def test_chat_service_reuses_same_agent():

    service = ChatService()

    first_agent = service.get_agent("conversation_a")
    second_agent = service.get_agent("conversation_a")

    assert first_agent is second_agent


def test_chat_service_rejects_empty_conversation_id():

    service = ChatService()

    try:
        service.get_agent("")
        assert False
    except ValueError as exc:
        assert "conversation_id cannot be empty" in str(exc)


@pytest.mark.anyio
async def test_chat_service_rejects_empty_message():

    service = ChatService()

    try:
        await service.chat(
            "conversation_a",
            ""
        )
        assert False
    except ValueError as exc:
        assert "message cannot be empty" in str(exc)