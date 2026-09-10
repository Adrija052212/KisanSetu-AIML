from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_real_ai_chat():
    response = client.post(
        "/ai/chat",
        json={
            "conversation_id": "real_test_001",
            "message": "What can KisanSetu help me with?",
            "language": "English",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] == "real_test_001"
    assert data["response"]
    assert data["language"] == "English"

    print("\nClaude response:")
    print(data["response"])