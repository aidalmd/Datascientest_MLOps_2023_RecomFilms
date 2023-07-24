import pytest
from fastapi.testclient import TestClient
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from api import (
    app,
    API_KEY_NAME 
)

# Create a test client using TestClient and pass the FastAPI app to it.
client = TestClient(app)

def test_get_current_user():
    """
    Unit test function to check the 'GET /users/me' endpoint,
    which retrieves the current user.
    """
    # Test without authentication (should return 401 Unauthorized)
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Test with invalid credentials (should return 401 Unauthorized)
    response = client.get("/users/me", auth=("invalid_username", "invalid_password"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

    # Test with valid credentials (should return 200 OK)
    response = client.get("/users/me", auth=("hello", "1234"))
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "password" in data
    assert data["username"] == "hello"
    assert data["password"] == "1234"

def test_recommend_films():
    """
    Test function to check the 'POST /api/v1/recommendations' endpoint,
    which recommends films based on the input title.
    """
    # Test without authentication (should return 401 Unauthorized)
    response = client.post("/api/v1/recommendations", json={"title": "Avatar"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Test with valid credentials (should return 200 OK)
    response = client.post("/api/v1/recommendations", json={"title": "Avatar"}, auth=("hello", "1234"))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Should return a list of recommended film titles
    assert all(isinstance(item, str) for item in data)  # All items in the list should be strings
    assert len(data) > 0  # The list should not be empty


def test_predictions():
    """
    Test function to check the 'POST /api/v1/recommendations/predictions' endpoint,
    which predicts film recommendations based on the input title.
    """
    # Test without authentication (should return 401 Unauthorized)
    response = client.post("/api/v1/recommendations/predictions", json={"title": "Avatar"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Test with valid credentials (should return 200 OK)
    response = client.post("/api/v1/recommendations/predictions", json={"title": "Avatar"}, auth=("hello", "1234"))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)  # Should return a dictionary containing recommendation details
    assert "recom_date" in data
    assert "user_film" in data
    assert "recommended_films" in data
    assert "recommended_ratings" in data
    assert isinstance(data["recom_date"], str)  # Recommendation date should be a string
    assert isinstance(data["user_film"], str)  # User's film should be a string
    assert isinstance(data["recommended_films"], list)  # Recommended films should be a list
    assert isinstance(data["recommended_ratings"], list)  # Recommended ratings should be a list
    assert len(data["recommended_films"]) == len(data["recommended_ratings"])  # Both lists should have the same length
    assert len(data["recommended_films"]) > 0  # The recommended films list should not be empty
    
# run pytest, 3 passed