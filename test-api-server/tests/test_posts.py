from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from main import app


@pytest.fixture
def client():

    # drop db before test - this is not ideal but good for poc
    Path("database.db").unlink(missing_ok=True)

    with TestClient(app) as c:
        yield c


def test_get_posts(client: TestClient):

    response = client.get("/posts")
    assert response.status_code == 200
    assert response.json() == []


def test_create_post(client: TestClient):
    response = client.post("/posts", json={"title": "Test Post", "content": "Test Content", "author": "Test Author"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "Test Content"
    assert data["author"] == "Test Author"
    assert data["id"]
    assert data["created_at"]
    assert data["edited_at"]

    response = client.get("/posts/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "Test Content"
    assert data["author"] == "Test Author"
    assert data["id"] == 1
    assert data["created_at"]
    assert data["edited_at"]

    response = client.put("/posts/1", json={"title": "Updated Post", "content": "Updated Content", "author": "Updated Author"})
    assert response.status_code == 200
    up_data = response.json()
    assert up_data["title"] == "Updated Post"
    assert up_data["content"] == "Updated Content"
    assert up_data["author"] == "Updated Author"
    assert up_data["id"] == 1
    assert up_data["created_at"] == data["created_at"]
    assert up_data["edited_at"] != data["edited_at"]


def test_not_found(client: TestClient):

    response = client.get("/posts/1")
    assert response.status_code == 404

    response = client.put("/posts/1", json={"title": "Updated Post", "content": "Updated Content", "author": "Updated Author"})
    assert response.status_code == 404


def test_validation_errors(client: TestClient):
    response = client.post("/posts", json={"title": "", "content": "Test Content", "author": "Test Author"})
    assert response.status_code == 422
    assert "String must not be empty" in response.json()["detail"][0]["msg"]

    response = client.post("/posts", json={"title": "Test Post", "content": "", "author": "Test Author"})
    assert response.status_code == 422
    assert "String must not be empty" in response.json()["detail"][0]["msg"]
    
