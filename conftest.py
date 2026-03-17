"""
Pytest configuration and shared fixtures
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.models import Base
from app.db.database import get_db
from main import app

# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client with dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(client):
    """Register and return a test user with token"""
    email = "test@example.com"
    password = "testpass123"
    
    # Register
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert response.status_code == 201
    user = response.json()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    return {
        "id": user["id"],
        "email": user["email"],
        "token": token,
        "password": password,
    }

@pytest.fixture
def auth_headers(test_user):
    """Return authorization headers for test user"""
    return {"Authorization": f"Bearer {test_user['token']}"}

@pytest.fixture
def test_user_2(client):
    """Register and return a second test user"""
    email = "test2@example.com"
    password = "testpass456"
    
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    assert response.status_code == 201
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    
    return {
        "id": login_response.json()["sub"],
        "email": email,
        "token": login_response.json()["access_token"],
    }

@pytest.fixture
def test_tag(client, auth_headers):
    """Create and return a test tag"""
    response = client.post(
        "/api/v1/tags",
        headers=auth_headers,
        json={"name": "work", "color": "#FF5733"}
    )
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def test_todo(client, auth_headers, test_tag):
    """Create and return a test todo"""
    response = client.post(
        "/api/v1/todos",
        headers=auth_headers,
        json={
            "title": "Test Todo",
            "description": "Test Description",
            "tag_ids": [test_tag["id"]]
        }
    )
    assert response.status_code == 201
    return response.json()
