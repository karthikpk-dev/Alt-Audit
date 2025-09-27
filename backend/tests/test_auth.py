import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.auth import get_password_hash, verify_password, create_access_token, verify_token

def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_jwt_token_creation():
    """Test JWT token creation and verification."""
    user_id = 1
    token = create_access_token(data={"sub": str(user_id)})
    
    assert token is not None
    assert isinstance(token, str)
    
    # Verify token
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)

def test_jwt_token_verification_invalid():
    """Test JWT token verification with invalid token."""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(Exception):
        verify_token(invalid_token)

def test_register_user(client: TestClient, db_session: Session):
    """Test user registration."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123"
    }
    
    response = client.post("/api/v1/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data  # Password should not be returned

def test_register_user_duplicate_username(client: TestClient, test_user):
    """Test user registration with duplicate username."""
    user_data = {
        "username": test_user.username,
        "email": "different@example.com",
        "password": "password123"
    }
    
    response = client.post("/api/v1/register", json=user_data)
    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()

def test_register_user_duplicate_email(client: TestClient, test_user):
    """Test user registration with duplicate email."""
    user_data = {
        "username": "differentuser",
        "email": test_user.email,
        "password": "password123"
    }
    
    response = client.post("/api/v1/register", json=user_data)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()

def test_register_user_invalid_email(client: TestClient):
    """Test user registration with invalid email."""
    user_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "password123"
    }
    
    response = client.post("/api/v1/register", json=user_data)
    assert response.status_code == 422

def test_register_user_weak_password(client: TestClient):
    """Test user registration with weak password."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123"  # Too short
    }
    
    response = client.post("/api/v1/register", json=user_data)
    assert response.status_code == 422

def test_login_success(client: TestClient, test_user):
    """Test successful login."""
    login_data = {
        "username": test_user.username,
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

def test_login_invalid_username(client: TestClient):
    """Test login with invalid username."""
    login_data = {
        "username": "nonexistent",
        "password": "password123"
    }
    
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == 401

def test_login_invalid_password(client: TestClient, test_user):
    """Test login with invalid password."""
    login_data = {
        "username": test_user.username,
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == 401

def test_login_json_success(client: TestClient, test_user):
    """Test JSON login endpoint."""
    login_data = {
        "username": test_user.username,
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/login-json", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client: TestClient, auth_headers, test_user):
    """Test getting current user information."""
    response = client.get("/api/v1/me", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert "created_at" in data

def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/me")
    assert response.status_code == 401

def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token."""
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == 401

def test_refresh_token(client: TestClient, auth_headers):
    """Test token refresh."""
    response = client.post("/api/v1/refresh", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_refresh_token_unauthorized(client: TestClient):
    """Test token refresh without authentication."""
    response = client.post("/api/v1/refresh")
    assert response.status_code == 401

def test_user_creation_in_database(db_session: Session):
    """Test that user is properly created in database."""
    user = User(
        username="dbtest",
        email="dbtest@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.username == "dbtest"
    assert user.email == "dbtest@example.com"
    assert user.is_active is True
    assert user.created_at is not None

def test_user_password_verification(db_session: Session):
    """Test password verification with database user."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    user = User(
        username="passtest",
        email="passtest@example.com",
        hashed_password=hashed,
        is_active=True
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert verify_password(password, user.hashed_password)
    assert not verify_password("wrongpassword", user.hashed_password)

def test_user_inactive_login(client: TestClient, db_session: Session):
    """Test login with inactive user."""
    user = User(
        username="inactive",
        email="inactive@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=False
    )
    
    db_session.add(user)
    db_session.commit()
    
    login_data = {
        "username": "inactive",
        "password": "password123"
    }
    
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == 401

def test_token_expiration():
    """Test token expiration handling."""
    import time
    from app.config import settings
    
    # Create token with very short expiration
    original_expire = settings.access_token_expire_minutes
    settings.access_token_expire_minutes = 0.001  # Very short expiration
    
    token = create_access_token(data={"sub": "1"})
    
    # Wait for token to expire
    time.sleep(0.1)
    
    with pytest.raises(Exception):
        verify_token(token)
    
    # Restore original setting
    settings.access_token_expire_minutes = original_expire
