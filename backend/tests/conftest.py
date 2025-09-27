import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User, ScanResult, ImageDetail
from app.auth import get_password_hash
from app.config import settings

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    """Create a database session for testing."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user_2(db_session):
    """Create a second test user."""
    user = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=get_password_hash("testpassword2"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_scan_result(db_session, test_user):
    """Create a test scan result."""
    scan = ScanResult(
        url="https://example.com",
        user_id=test_user.id,
        total_images=10,
        images_with_alt=7,
        images_missing_alt=3,
        coverage_percentage=70.0,
        status="completed"
    )
    db_session.add(scan)
    db_session.commit()
    db_session.refresh(scan)
    return scan

@pytest.fixture
def test_image_details(db_session, test_scan_result):
    """Create test image details."""
    images = [
        ImageDetail(
            scan_id=test_scan_result.id,
            image_url="https://example.com/image1.jpg",
            alt_text="Test image 1",
            has_alt=True,
            is_decorative=False,
            width=100,
            height=100
        ),
        ImageDetail(
            scan_id=test_scan_result.id,
            image_url="https://example.com/image2.jpg",
            alt_text="",
            has_alt=True,
            is_decorative=True,
            width=200,
            height=200
        ),
        ImageDetail(
            scan_id=test_scan_result.id,
            image_url="https://example.com/image3.jpg",
            alt_text=None,
            has_alt=False,
            is_decorative=False,
            width=300,
            height=300
        )
    ]
    
    for image in images:
        db_session.add(image)
    db_session.commit()
    
    for image in images:
        db_session.refresh(image)
    
    return images

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/login",
        data={"username": test_user.username, "password": "testpassword"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_2(client, test_user_2):
    """Get authentication headers for second test user."""
    response = client.post(
        "/api/v1/login",
        data={"username": test_user_2.username, "password": "testpassword2"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Test Page</h1>
        <img src="https://example.com/image1.jpg" alt="Test image 1" width="100" height="100">
        <img src="https://example.com/image2.jpg" alt="" width="200" height="200">
        <img src="https://example.com/image3.jpg" width="300" height="300">
        <div style="background-image: url('https://example.com/bg.jpg')">Background image</div>
    </body>
    </html>
    """

@pytest.fixture
def sample_html_with_css_images():
    """Sample HTML with CSS background images."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page with CSS Images</title>
        <style>
            .bg-image {
                background-image: url('https://example.com/bg1.jpg');
            }
            .bg-image-2 {
                background-image: url('https://example.com/bg2.jpg');
            }
        </style>
    </head>
    <body>
        <h1>Test Page</h1>
        <div class="bg-image">Background 1</div>
        <div class="bg-image-2">Background 2</div>
    </body>
    </html>
    """

@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing."""
    from unittest.mock import AsyncMock, MagicMock
    
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><img src='test.jpg' alt='test'></body></html>"
    mock_response.headers = {"content-type": "text/html"}
    
    mock_client.get.return_value = mock_response
    return mock_client

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    from unittest.mock import MagicMock
    
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.exists.return_value = False
    mock_redis.incr.return_value = 1
    mock_redis.expire.return_value = True
    
    return mock_redis
