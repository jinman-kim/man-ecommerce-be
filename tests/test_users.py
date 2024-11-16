from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users/", json={"email": "user@example.com", "password": "secret"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
