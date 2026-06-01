import pytest
import os
import sys
import tempfile

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'phase4'))

from phase4.database import Database
from phase4.auth import AuthManager, AuthenticationError


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = Database(db_path)
    yield db
    
    db.close()
    os.unlink(db_path)


@pytest.fixture
def auth_manager(temp_db):
    """Create an auth manager for testing."""
    return AuthManager(temp_db)


class TestAuthManager:
    """Test authentication operations."""
    
    def test_hash_password(self, auth_manager):
        """Test password hashing."""
        password = "test_password_123"
        hashed = auth_manager.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20
    
    def test_verify_password(self, auth_manager):
        """Test password verification."""
        password = "test_password_123"
        hashed = auth_manager.hash_password(password)
        
        assert auth_manager.verify_password(password, hashed) is True
        assert auth_manager.verify_password("wrong_password", hashed) is False
    
    def test_create_access_token(self, auth_manager):
        """Test JWT token creation."""
        data = {"sub": "testuser", "user_id": 1}
        token = auth_manager.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50
    
    def test_decode_access_token(self, auth_manager):
        """Test JWT token decoding."""
        data = {"sub": "testuser", "user_id": 1}
        token = auth_manager.create_access_token(data)
        
        decoded = auth_manager.decode_access_token(token)
        
        assert decoded is not None
        assert decoded['sub'] == 'testuser'
        assert decoded['user_id'] == 1
    
    def test_decode_invalid_token(self, auth_manager):
        """Test decoding an invalid token."""
        invalid_token = "invalid_token_string"
        decoded = auth_manager.decode_access_token(invalid_token)
        
        assert decoded is None
    
    def test_register_user(self, auth_manager):
        """Test user registration."""
        result = auth_manager.register_user(
            username="newuser",
            password="password123",
            email="newuser@example.com"
        )
        
        assert result['username'] == 'newuser'
        assert result['email'] == 'newuser@example.com'
        assert result['id'] > 0
    
    def test_register_short_username(self, auth_manager):
        """Test registration with short username."""
        with pytest.raises(AuthenticationError) as exc_info:
            auth_manager.register_user("ab", "password123")
        
        assert "at least 3 characters" in str(exc_info.value)
    
    def test_register_short_password(self, auth_manager):
        """Test registration with short password."""
        with pytest.raises(AuthenticationError) as exc_info:
            auth_manager.register_user("validuser", "short")
        
        assert "at least 8 characters" in str(exc_info.value)
    
    def test_register_duplicate_user(self, auth_manager):
        """Test registering a duplicate username."""
        auth_manager.register_user("duplicate", "password123")
        
        with pytest.raises(AuthenticationError) as exc_info:
            auth_manager.register_user("duplicate", "password456")
        
        assert "already exists" in str(exc_info.value)
    
    def test_authenticate_user(self, auth_manager):
        """Test user authentication."""
        # First register a user
        auth_manager.register_user("authuser", "authpass123", "auth@example.com")
        
        # Then authenticate
        result = auth_manager.authenticate_user("authuser", "authpass123")
        
        assert result is not None
        assert result['username'] == 'authuser'
        assert 'access_token' in result
        assert result['token_type'] == 'bearer'
    
    def test_authenticate_wrong_password(self, auth_manager):
        """Test authentication with wrong password."""
        auth_manager.register_user("wrongpass", "correctpass")
        
        result = auth_manager.authenticate_user("wrongpass", "wrongpass")
        
        assert result is None
    
    def test_authenticate_nonexistent_user(self, auth_manager):
        """Test authentication with nonexistent user."""
        result = auth_manager.authenticate_user("nonexistent", "password")
        
        assert result is None
    
    def test_get_current_user(self, auth_manager):
        """Test getting current user from token."""
        # Register and authenticate
        auth_manager.register_user("currentuser", "currentpass123")
        result = auth_manager.authenticate_user("currentuser", "currentpass123")
        
        # Get current user from token
        user = auth_manager.get_current_user(result['access_token'])
        
        assert user is not None
        assert user['username'] == 'currentuser'
    
    def test_get_current_user_invalid_token(self, auth_manager):
        """Test getting current user with invalid token."""
        user = auth_manager.get_current_user("invalid_token")
        
        assert user is None
