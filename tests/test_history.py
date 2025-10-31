from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_history_endpoint():
    # check endpoint works
    resp = client.get("/history")
    assert resp.status_code == 200
    data = resp.json()
    assert "history" in data


