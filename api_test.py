import pytest
from starlette.testclient import TestClient
from api import api, connection

# Create a test client using FastAPI's TestClient
client = TestClient(api)


def test_create_user():
    response = client.post(
        "/api/v1/users",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully."}


def test_create_user_existing_username():
    # Assuming the "testuser" already exists in the database
    response = client.post(
        "/api/v1/users",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Username already taken."}


def test_get_users():
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    # Assuming the response contains a "users" key that holds a list of users
    assert isinstance(response.json().get("users"), list)


def test_delete_user():
    # Assuming the "testuser" exists in the database
    # You need to fetch the user_id dynamically or use a known user_id for testing
    user_id = "123e4567-e89b-12d3-a456-426655440000"
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}


def test_delete_user_not_found():
    # Assuming the user_id doesn't exist in the database
    user_id = "nonexistent-user-id"
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
