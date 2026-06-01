import hashlib
import secrets
from typing import Optional, Dict
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import streamlit as st


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthManager:
    """Manage user authentication and sessions."""
    
    def __init__(self, database):
        """Initialize authentication manager.
        
        Args:
            database: Database instance for user storage
        """
        self.db = database
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Optional[Dict]:
        """Decode and verify a JWT access token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def register_user(self, username: str, password: str, email: Optional[str] = None) -> Dict:
        """Register a new user.
        
        Args:
            username: Username
            password: Plain text password
            email: Email address (optional)
            
        Returns:
            User information dictionary
            
        Raises:
            AuthenticationError: If registration fails
        """
        # Validate username
        if not username or len(username) < 3:
            raise AuthenticationError("Username must be at least 3 characters")
        
        # Validate password
        if not password or len(password) < 8:
            raise AuthenticationError("Password must be at least 8 characters")
        
        # Check if user already exists
        existing_user = self.db.get_user(username)
        if existing_user:
            raise AuthenticationError("Username already exists")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Add user to database
        user_id = self.db.add_user(username, password_hash, email)
        
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "message": "User registered successfully"
        }
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User information with access token if successful, None otherwise
        """
        # Get user from database
        user = self.db.get_user(username)
        
        if not user:
            return None
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            return None
        
        # Update last login
        self.db.update_user_login(username)
        
        # Create access token
        access_token = self.create_access_token(
            data={"sub": username, "user_id": user['id']}
        )
        
        return {
            "id": user['id'],
            "username": user['username'],
            "email": user.get('email'),
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    def get_current_user(self, token: str) -> Optional[Dict]:
        """Get current user from access token.
        
        Args:
            token: JWT access token
            
        Returns:
            User information or None if invalid
        """
        payload = self.decode_access_token(token)
        
        if payload is None:
            return None
        
        username = payload.get("sub")
        
        if username is None:
            return None
        
        user = self.db.get_user(username)
        
        if user is None:
            return None
        
        return {
            "id": user['id'],
            "username": user['username'],
            "email": user.get('email')
        }


# Streamlit Authentication Helpers

def init_streamlit_auth():
    """Initialize Streamlit authentication session state."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'token' not in st.session_state:
        st.session_state.token = None


def login_page(database):
    """Display login page.
    
    Args:
        database: Database instance
    """
    st.title("🔐 Login")
    st.markdown("---")
    
    auth_manager = AuthManager(database)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                result = auth_manager.authenticate_user(username, password)
                
                if result:
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "id": result['id'],
                        "username": result['username'],
                        "email": result.get('email')
                    }
                    st.session_state.token = result['access_token']
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    st.markdown("---")
    st.subheader("Don't have an account?")
    if st.button("Register", use_container_width=True):
        st.session_state.show_register = True
        st.rerun()


def register_page(database):
    """Display registration page.
    
    Args:
        database: Database instance
    """
    st.title("📝 Register")
    st.markdown("---")
    
    auth_manager = AuthManager(database)
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username (min 3 characters)")
        email = st.text_input("Email (optional)", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Choose a password (min 8 characters)")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submit_button = st.form_submit_button("Register", use_container_width=True)
        
        if submit_button:
            if not username or len(username) < 3:
                st.error("Username must be at least 3 characters")
            elif not password or len(password) < 8:
                st.error("Password must be at least 8 characters")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                try:
                    result = auth_manager.register_user(username, password, email)
                    st.success(f"Registration successful! You can now login as {username}")
                    st.session_state.show_register = False
                    st.rerun()
                except AuthenticationError as e:
                    st.error(str(e))
    
    st.markdown("---")
    st.subheader("Already have an account?")
    if st.button("Login", use_container_width=True):
        st.session_state.show_register = False
        st.rerun()


def logout():
    """Logout current user."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.success("Logged out successfully")
    st.rerun()


def require_auth(database):
    """Decorator to require authentication for Streamlit pages.
    
    Args:
        database: Database instance
        
    Returns:
        True if authenticated, False otherwise
    """
    init_streamlit_auth()
    
    if not st.session_state.authenticated:
        if getattr(st.session_state, 'show_register', False):
            register_page(database)
        else:
            login_page(database)
        return False
    
    return True


def auth_sidebar():
    """Display authentication information in sidebar."""
    if st.session_state.authenticated and st.session_state.user:
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"👤 {st.session_state.user['username']}")
        st.sidebar.caption(f"ID: {st.session_state.user['id']}")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
