import os
import random
import string
import uuid
from config import SUPERUSER_EMAIL, SUPERUSER_PASSWORD
import pytest
import requests
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
BASE_URL = "http://localhost:8000"  # Change to your API base URL
API_V1_STR = "/api/v1"


# --- Helper Functions (Reused Code) ---

def random_lower_string(length: int = 12) -> str:
    """Generate a random string of lowercase letters."""
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))


def random_email() -> str:
    """Generate a random email address."""
    return f"{random_lower_string()}@test-api.com"


def get_auth_headers(email: str, password: str) -> dict[str, str]:
    """Authenticate a user and return authorization headers."""
    login_data = {"username": email, "password": password}
    try:
        response = requests.post(
            f"{BASE_URL}{API_V1_STR}/login/access-token", data=login_data
        )
        response.raise_for_status()
        tokens = response.json()
        access_token = tokens["access_token"]
        return {"Authorization": f"Bearer {access_token}"}
    except requests.exceptions.ConnectionError as e:
        pytest.fail(
            f"API request failed during authentication for {email}. "
            f"Is the server running at {BASE_URL}? Error: {e}"
        )
    # Let HTTPError and other exceptions propagate for test assertions


def get_superuser_auth_headers() -> dict[str, str]:
    """Get auth headers for the default superuser."""
    return get_auth_headers(SUPERUSER_EMAIL, SUPERUSER_PASSWORD)


def create_user_and_get_headers(
    full_name: str, email: str, password: str
) -> dict[str, str]:
    """Helper to register a new user and return their auth headers."""
    user_payload = {"full_name": full_name, "email": email, "password": password}
    response = requests.post(f"{BASE_URL}{API_V1_STR}/users/signup", json=user_payload)
    assert response.status_code == 200, f"Failed to sign up user {email}"
    return get_auth_headers(email, password)

@pytest.mark.integration
class TestAPI:
    """A suite of 15 integration tests for the FastAPI backend API."""

    # Test Case 1: Superuser Login
    def test_superuser_login(self):
        """Tests that the superuser can log in and receive an access token."""
        headers = get_superuser_auth_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")

    # Test Case 2: Invalid Login
    def test_invalid_login(self):
        """Tests that login fails with incorrect credentials."""
        with pytest.raises(requests.exceptions.HTTPError) as excinfo:
            get_auth_headers("wrong@email.com", "wrongpassword")
        assert excinfo.value.response.status_code == 400

    # Test Case 3: Superuser Access to List Users
    def test_superuser_can_read_users(self):
        """Tests that a superuser can access the admin endpoint to list all users."""
        headers = get_superuser_auth_headers()
        response = requests.get(f"{BASE_URL}{API_V1_STR}/users/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data and isinstance(data["data"], list)
        assert "count" in data

    # Test Case 4: Normal User Cannot Access Admin Endpoints
    def test_normal_user_cannot_read_users(self):
        """Tests that a regular user is forbidden from listing all users."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Normal User", email, password)

        response = requests.get(f"{BASE_URL}{API_V1_STR}/users/", headers=headers)
        assert response.status_code == 403
        assert response.json()["detail"] == "The user doesn't have enough privileges"

    # Test Case 5: Superuser Can Create a New User
    def test_superuser_can_create_user(self):
        """Tests that a superuser can successfully create a new user."""
        headers = get_superuser_auth_headers()
        email, password = random_email(), random_lower_string()
        payload = {
            "email": email,
            "password": password,
            "full_name": "Created by Admin",
        }

        response = requests.post(
            f"{BASE_URL}{API_V1_STR}/users/", headers=headers, json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["full_name"] == "Created by Admin"

    # Test Case 6: User Self-Registration (Signup)
    def test_user_signup(self):
        """Tests the public signup endpoint for new user registration."""
        email, password, full_name = random_email(), random_lower_string(), "New Signee"
        payload = {"email": email, "password": password, "full_name": full_name}

        response = requests.post(
            f"{BASE_URL}{API_V1_STR}/users/signup", json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email

    # Test Case 7: Reading Own User Profile
    def test_user_can_read_own_profile(self):
        """Tests that an authenticated user can read their own profile via /users/me."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Profile User", email, password)

        response = requests.get(f"{BASE_URL}{API_V1_STR}/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email

    # Test Case 8: Updating Own User Profile
    def test_user_can_update_own_profile(self):
        """Tests that a user can update their full_name via /users/me."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Original Name", email, password)

        payload = {"full_name": "Updated Name"}
        response = requests.patch(
            f"{BASE_URL}{API_V1_STR}/users/me", headers=headers, json=payload
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    # Test Case 9: Superuser Can Delete a User
    def test_superuser_can_delete_user(self):
        """Tests that a superuser can delete another user."""
        email, password = random_email(), random_lower_string()
        create_user_and_get_headers("User To Delete", email, password)

        admin_headers = get_superuser_auth_headers()
        users_response = requests.get(
            f"{BASE_URL}{API_V1_STR}/users/", headers=admin_headers
        )
        user_to_delete = next(
            u for u in users_response.json()["data"] if u["email"] == email
        )
        user_id = user_to_delete["id"]

        response = requests.delete(
            f"{BASE_URL}{API_V1_STR}/users/{user_id}", headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"

    # Test Case 10: User Can Delete Their Own Account
    def test_user_can_delete_self(self):
        """Tests that a regular user can delete their own account via /users/me."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Self Destruct", email, password)

        response = requests.delete(f"{BASE_URL}{API_V1_STR}/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"

        # Verify login fails after deletion
        with pytest.raises(requests.exceptions.HTTPError):
            get_auth_headers(email, password)

    # Test Case 11: Create Item
    def test_user_can_create_item(self):
        """Tests that an authenticated user can create a new item."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Item Creator", email, password)

        payload = {"title": "My First Item", "description": "This is a test item."}
        response = requests.post(
            f"{BASE_URL}{API_V1_STR}/items/", headers=headers, json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My First Item"
        assert "id" in data

    # Test Case 12: Read Items (Own Items)
    def test_user_can_read_own_items(self):
        """Tests that a user can retrieve a list of their own items."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Item Lister", email, password)

        # Create an item first
        requests.post(
            f"{BASE_URL}{API_V1_STR}/items/", headers=headers, json={"title": "Item 1"}
        )

        response = requests.get(f"{BASE_URL}{API_V1_STR}/items/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert data["data"][0]["title"] == "Item 1"

    # Test Case 13: Update Item
    def test_user_can_update_own_item(self):
        """Tests that a user can update an item they own."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Item Updater", email, password)

        create_response = requests.post(
            f"{BASE_URL}{API_V1_STR}/items/",
            headers=headers,
            json={"title": "Original Title"},
        )
        item_id = create_response.json()["id"]

        update_payload = {"title": "Updated Title"}
        response = requests.put(
            f"{BASE_URL}{API_V1_STR}/items/{item_id}",
            headers=headers,
            json=update_payload,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    # Test Case 14: Delete Item
    def test_user_can_delete_own_item(self):
        """Tests that a user can delete an item they own."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Item Deleter", email, password)

        create_response = requests.post(
            f"{BASE_URL}{API_V1_STR}/items/",
            headers=headers,
            json={"title": "To Be Deleted"},
        )
        item_id = create_response.json()["id"]

        response = requests.delete(
            f"{BASE_URL}{API_V1_STR}/items/{item_id}", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Item deleted successfully"

    # Test Case 15: Health Check Endpoint
    def test_health_check(self):
        """Tests the public health check endpoint."""
        response = requests.get(f"{BASE_URL}{API_V1_STR}/utils/health-check/")
        assert response.status_code == 200
        assert response.json() is True
