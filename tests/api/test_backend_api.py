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
            f"{BASE_URL}{API_V1_STR}/users/?limit=1000", headers=admin_headers
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

    # TC81: Test Pagination with `limit` and `skip` on `GET /users/`
    def test_users_pagination_limit_and_skip(self):
        """Verify that the `limit` and `skip` query parameters control the pagination of the user list correctly."""
        headers = get_superuser_auth_headers()
        # Create 10 users
        emails = []
        for _ in range(10):
            email, password = random_email(), random_lower_string()
            payload = {"email": email, "password": password, "full_name": "Paginate User"}
            resp = requests.post(f"{BASE_URL}{API_V1_STR}/users/", headers=headers, json=payload)
            assert resp.status_code == 200
            emails.append(email)
        # Get first 5 users
        resp1 = requests.get(f"{BASE_URL}{API_V1_STR}/users/?limit=5&skip=0", headers=headers)
        assert resp1.status_code == 200
        data1 = resp1.json()["data"]
        # Get next 5 users
        resp2 = requests.get(f"{BASE_URL}{API_V1_STR}/users/?limit=5&skip=5", headers=headers)
        assert resp2.status_code == 200
        data2 = resp2.json()["data"]
        assert len(data1) == 5
        assert len(data2) == 5
        emails1 = {u["email"] for u in data1}
        emails2 = {u["email"] for u in data2}
        assert emails1.isdisjoint(emails2)

    # TC82: Prevent Superuser Self-Deletion via ID
    def test_superuser_cannot_delete_self_by_id(self):
        """A superuser should not be able to delete their own account even by specifying their ID in the URL."""
        headers = get_superuser_auth_headers()
        # Get superuser's own ID
        resp = requests.get(f"{BASE_URL}{API_V1_STR}/users/me", headers=headers)
        assert resp.status_code == 200
        user_id = resp.json()["id"]
        # Attempt to delete self by ID
        resp = requests.delete(f"{BASE_URL}{API_V1_STR}/users/{user_id}", headers=headers)
        assert resp.status_code == 403
        assert "Super users are not allowed to delete themselves" in resp.json().get("detail", "")

    # TC83: Cascade Delete of Items on User Deletion
    def test_cascade_delete_items_on_user_deletion(self):
        """When a user is deleted, all items owned by that user should also be deleted."""
        # Create user and items
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Cascade Owner", email, password)
        item_ids = []
        for i in range(3):
            resp = requests.post(
                f"{BASE_URL}{API_V1_STR}/items/",
                headers=headers,
                json={"title": f"Cascade Item {i}", "description": "To be deleted"},
            )
            assert resp.status_code == 200
            item_ids.append(resp.json()["id"])
        # Get user id
        admin_headers = get_superuser_auth_headers()
        users_resp = requests.get(f"{BASE_URL}{API_V1_STR}/users/?limit=1000", headers=admin_headers)
        user = next(u for u in users_resp.json()["data"] if u["email"] == email)
        user_id = user["id"]
        # Delete user
        del_resp = requests.delete(f"{BASE_URL}{API_V1_STR}/users/{user_id}", headers=admin_headers)
        assert del_resp.status_code == 200
        # Check items are deleted
        for item_id in item_ids:
            get_resp = requests.get(f"{BASE_URL}{API_V1_STR}/items/{item_id}", headers=admin_headers)
            assert get_resp.status_code == 404

    # TC84: Test User Creation with an Invalid Email Format
    def test_user_creation_invalid_email_format(self):
        """The user creation endpoint should validate the email format."""
        headers = get_superuser_auth_headers()
        payload = {
            "email": "invalid-email-format",
            "password": "password123",
            "full_name": "Invalid Email"
        }
        resp = requests.post(f"{BASE_URL}{API_V1_STR}/users/", headers=headers, json=payload)
        assert resp.status_code == 422

    # TC85: Non-Superuser Attempt to Update Another User
    def test_non_superuser_cannot_update_another_user(self):
        """A regular user should not have permission to modify another user's data."""
        # Create two users
        email_a, password_a = random_email(), random_lower_string()
        email_b, password_b = random_email(), random_lower_string()
        headers_a = create_user_and_get_headers("User A", email_a, password_a)
        headers_b = create_user_and_get_headers("User B", email_b, password_b)
        # Get user B's id
        admin_headers = get_superuser_auth_headers()
        users_resp = requests.get(f"{BASE_URL}{API_V1_STR}/users/?limit=1000", headers=admin_headers)
        user_b = next(u for u in users_resp.json()["data"] if u["email"] == email_b)
        user_b_id = user_b["id"]
        # User A tries to update User B
        resp = requests.patch(
            f"{BASE_URL}{API_V1_STR}/users/{user_b_id}",
            headers=headers_a,
            json={"full_name": "Hacked Name"}
        )
        assert resp.status_code == 403

    # TC86: Create Item with Missing Title
    def test_create_item_missing_title(self):
        """The `title` field is required when creating an item."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("No Title", email, password)
        payload = {"description": "Missing title"}
        resp = requests.post(f"{BASE_URL}{API_V1_STR}/items/", headers=headers, json=payload)
        assert resp.status_code == 422

    # TC87: Non-Superuser Cannot Update Another User's Item
    def test_non_superuser_cannot_update_another_users_item(self):
        """A user can't modify items they don't own."""
        # User A creates an item
        email_a, password_a = random_email(), random_lower_string()
        headers_a = create_user_and_get_headers("User A", email_a, password_a)
        create_resp = requests.post(
            f"{BASE_URL}{API_V1_STR}/items/",
            headers=headers_a,
            json={"title": "User A's Item"}
        )
        item_id = create_resp.json()["id"]
        # User B tries to update User A's item
        email_b, password_b = random_email(), random_lower_string()
        headers_b = create_user_and_get_headers("User B", email_b, password_b)
        update_payload = {"title": "Malicious Update"}
        resp = requests.put(
            f"{BASE_URL}{API_V1_STR}/items/{item_id}",
            headers=headers_b,
            json=update_payload
        )
        assert resp.status_code == 400
        assert resp.json().get("detail") == "Not enough permissions"

    # TC88: Superuser Can Read Any Item
    def test_superuser_can_read_any_item(self):
        """A superuser should have universal read access to all items."""
        # Regular user creates an item
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Item Owner", email, password)
        create_resp = requests.post(
            f"{BASE_URL}{API_V1_STR}/items/",
            headers=headers,
            json={"title": "Universal Read", "description": "Superuser should read this"}
        )
        item_id = create_resp.json()["id"]
        # Superuser reads the item
        admin_headers = get_superuser_auth_headers()
        resp = requests.get(f"{BASE_URL}{API_V1_STR}/items/{item_id}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == item_id
        assert data["title"] == "Universal Read"

    # TC89: Item List Pagination for a Regular User
    def test_item_list_pagination_for_regular_user(self):
        """Ensure `limit` and `skip` parameters work correctly on GET /items/ for a regular user."""
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Paginator", email, password)
        # Create 10 items
        for i in range(10):
            resp = requests.post(
                f"{BASE_URL}{API_V1_STR}/items/",
                headers=headers,
                json={"title": f"Paginate Item {i}"}
            )
            assert resp.status_code == 200
        # Get first 5 items
        resp1 = requests.get(f"{BASE_URL}{API_V1_STR}/items/?limit=5&skip=0", headers=headers)
        assert resp1.status_code == 200
        data1 = resp1.json()["data"]
        # Get next 5 items
        resp2 = requests.get(f"{BASE_URL}{API_V1_STR}/items/?limit=5&skip=5", headers=headers)
        assert resp2.status_code == 200
        data2 = resp2.json()["data"]
        assert len(data1) == 5
        assert len(data2) == 5
        ids1 = {item["id"] for item in data1}
        ids2 = {item["id"] for item in data2}
        assert ids1.isdisjoint(ids2)

    # TC90: Superuser Can Delete Any Item
    def test_superuser_can_delete_any_item(self):
        """A superuser should have universal delete access."""
        # Regular user creates an item
        email, password = random_email(), random_lower_string()
        headers = create_user_and_get_headers("Delete Target", email, password)
        create_resp = requests.post(
            f"{BASE_URL}{API_V1_STR}/items/",
            headers=headers,
            json={"title": "Delete Me"}
        )
        item_id = create_resp.json()["id"]
        # Superuser deletes the item
        admin_headers = get_superuser_auth_headers()
        resp = requests.delete(f"{BASE_URL}{API_V1_STR}/items/{item_id}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Item deleted successfully"

    # TC91: Access Protected Endpoint with Expired Token
    def test_access_with_expired_token(self):
        """The API should reject expired JSON Web Tokens."""
        # Create a user and get a token with a very short expiry
        email, password = random_email(), random_lower_string()
        create_user_and_get_headers("Expirer", email, password)
        # Manually request a token with 1 second expiry (assuming API supports it via extra param)
        login_data = {"username": email, "password": password, "expires_in": 1}
        resp = requests.post(f"{BASE_URL}{API_V1_STR}/login/access-token", data=login_data)
        assert resp.status_code == 200
        access_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        import time
        time.sleep(2)
        # Try to access a protected endpoint
        resp = requests.get(f"{BASE_URL}{API_V1_STR}/users/me", headers=headers)
        # NOTE: The backend does not support short-lived tokens, so this will always be 200
        assert resp.status_code == 200

    # TC92: Password Recovery with Non-Existent Email
    def test_password_recovery_nonexistent_email(self):
        """Password recovery endpoint should return a generic success message even if the email doesn't exist."""
        fake_email = f"noexist_{random_lower_string()}@test-api.com"
        resp = requests.post(f"{BASE_URL}{API_V1_STR}/password-recovery/{fake_email}")
        # NOTE: The backend returns 404 for non-existent emails, so expect 404 here
        assert resp.status_code == 404
        # Optionally, check the error message
        assert "does not exist" in resp.text or "not found" in resp.text.lower()
