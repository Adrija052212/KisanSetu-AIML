from fastapi.testclient import TestClient

from src.api.main import app, chat_service


client = TestClient(app)


def test_ai_chat_endpoint():

    original_chat = chat_service.chat

    async def fake_chat(
        conversation_id: str,
        message: str,
        language: str,
    ) -> str:
        return "Mock KisanSetu response."

    chat_service.chat = fake_chat

    try:
        response = client.post(
            "/ai/chat",
            json={
                "conversation_id": "conversation_001",
                "message": "Should I sell my tomato?",
                "language": "English",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["conversation_id"] == "conversation_001"
        assert data["response"] == "Mock KisanSetu response."
        assert data["language"] == "English"

    finally:
        chat_service.chat = original_chat


def test_ai_chat_rejects_empty_message():

    response = client.post(
        "/ai/chat",
        json={
            "conversation_id": "conversation_001",
            "message": "",
            "language": "English",
        },
    )

    assert response.status_code == 422