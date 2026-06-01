import pytest
import os
import sys
import tempfile
from fastapi.testclient import TestClient

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'phase4'))

# Import after path setup
from phase4.api.app import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def test_token(client):
    """Create a test user and return auth token."""
    # Register a test user
    response = client.post("/api/auth/register", params={
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    })
    
    # Login to get token
    response = client.post("/api/auth/login", params={
        "username": "testuser",
        "password": "testpass123"
    })
    
    return response.json()["data"]["access_token"]


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_register_user(self, client):
        """Test user registration."""
        response = client.post("/api/auth/register", params={
            "username": "newuser",
            "password": "newpass123",
            "email": "new@example.com"
        })
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_register_duplicate_user(self, client):
        """Test registering duplicate user."""
        # First registration
        client.post("/api/auth/register", params={
            "username": "dupuser",
            "password": "pass123"
        })
        
        # Second registration (should fail)
        response = client.post("/api/auth/register", params={
            "username": "dupuser",
            "password": "pass456"
        })
        
        assert response.status_code == 400
    
    def test_login(self, client):
        """Test user login."""
        # First register
        client.post("/api/auth/register", params={
            "username": "loginuser",
            "password": "loginpass123"
        })
        
        # Then login
        response = client.post("/api/auth/login", params={
            "username": "loginuser",
            "password": "loginpass123"
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()["data"]
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post("/api/auth/login", params={
            "username": "nonexistent",
            "password": "wrongpass"
        })
        
        assert response.status_code == 401
    
    def test_get_contacts_unauthorized(self, client):
        """Test getting contacts without authentication."""
        response = client.get("/api/contacts")
        assert response.status_code == 401
    
    def test_get_contacts_authorized(self, client, test_token):
        """Test getting contacts with authentication."""
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.get("/api/contacts", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_create_contact(self, client, test_token):
        """Test creating a contact."""
        headers = {"Authorization": f"Bearer {test_token}"}
        contact_data = {
            "recipient_email": "api@example.com",
            "recipient_name": "API User",
            "company": "API Company",
            "role": "Developer",
            "candidate_name": "Candidate",
            "candidate_background": "Python developer"
        }
        
        response = client.post("/api/contacts", json=contact_data, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_get_statistics(self, client, test_token):
        """Test getting statistics."""
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.get("/api/stats", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
    
    def test_generate_email(self, client, test_token):
        """Test email generation."""
        headers = {"Authorization": f"Bearer {test_token}"}
        contact_data = {
            "recipient_email": "gen@example.com",
            "recipient_name": "Gen User",
            "company": "Gen Company",
            "role": "Developer",
            "candidate_name": "Candidate",
            "candidate_background": "Python developer"
        }
        
        response = client.post("/api/generate", json=contact_data, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "subject" in response.json()["data"]
        assert "body" in response.json()["data"]
    
    def test_invalid_token(self, client):
        """Test using invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/contacts", headers=headers)
        
        assert response.status_code == 401
