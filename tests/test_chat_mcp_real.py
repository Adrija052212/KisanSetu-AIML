from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_real_ai_chat_with_buy_recommendation():
    response = client.post(
        "/ai/chat",
        json={
            "conversation_id": "mcp_test_001",
            "message": (
                "The current tomato price is Rs. 2000 per quintal "
                "and the predicted price is Rs. 2200 per quintal. "
                "I want to buy 10 quintals. Should I buy now or wait?"
            ),
            "language": "English",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] == "mcp_test_001"
    assert data["response"]
    assert data["language"] == "English"

    print("\nClaude + MCP response:")
    print(data["response"])