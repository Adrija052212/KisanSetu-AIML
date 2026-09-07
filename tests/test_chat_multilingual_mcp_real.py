from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_real_bengali_buy_recommendation():
    response = client.post(
        "/ai/chat",
        json={
            "conversation_id": "bengali_mcp_test_001",
            "message": (
                "বর্তমান টমেটোর দাম প্রতি কুইন্টালে ২০০০ টাকা "
                "এবং ভবিষ্যতের অনুমান করা দাম ২২০০ টাকা। "
                "আমার ১০ কুইন্টাল টমেটো কিনতে হবে। "
                "আমার কি এখনই কেনা উচিত, নাকি অপেক্ষা করা উচিত?"
            ),
            "language": "Bengali",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] == "bengali_mcp_test_001"
    assert data["response"]
    assert data["language"] == "Bengali"

    print("\nClaude Bengali + MCP response:")
    print(data["response"])