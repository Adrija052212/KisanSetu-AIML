from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_real_ai_chat_bengali():
    response = client.post(
        "/ai/chat",
        json={
            "conversation_id": "bengali_test_001",
            "message": "টমেটোর দাম বাড়তে পারে। আমার কি এখন টমেটো বিক্রি করা উচিত?",
            "language": "Bengali",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] == "bengali_test_001"
    assert data["response"]
    assert data["language"] == "Bengali"

    print("\nClaude Bengali response:")
    print(data["response"])