"""
Authentication and User endpoint tests
"""
import pytest


class TestAuthRegister:
    """Test user registration"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user["email"],
                "password": "anotherpass123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestAuthLogin:
    """Test user login"""
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_login_user_not_found(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


class TestAuthMe:
    """Test get current user endpoint"""
    
    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test getting current user info"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user["id"]
        assert data["email"] == test_user["email"]
        assert data["is_active"] is True
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token fails"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
