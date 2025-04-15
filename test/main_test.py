import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_image():
    with open("tests/test_image.jpg", "rb") as img:
        response = client.post(
            "/api/upload",
            files={"file": ("test.jpg", img, "image/jpeg")},
            data={"user_id": "user123", "description": "A test image", "tags": "test,fastapi"}
        )
    assert response.status_code == 200
    assert "image_url" in response.json()

def test_list_images():
    response = client.get("/api/images?user_id=user123")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_view_image_not_found():
    response = client.get("/api/image/nonexistent.jpg")
    assert response.status_code == 404

def test_delete_image_not_found():
    response = client.delete("/api/image/nonexistent.jpg")
    assert response.status_code in [200, 404]