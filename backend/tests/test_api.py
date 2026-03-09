from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root_returns_welcome_message():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_products_list_endpoint_exists():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
